"""A built image must carry its catalogue pin and a compiler of its own.

The registry fixtures are the manifest and config of the `rebrew/msvc:7.0-win32`
image that served the 7.1 compiler under the 7.0 tag (its build history checks
`msvc710`'s sha256); the engine is a stub of the Docker Engine API calls the
check makes.  Nothing here reaches a network or a container engine.
"""

from __future__ import annotations

import contextlib
import email.message
import importlib
import io
import json
import tarfile
import unittest
import urllib.error
import urllib.request
from collections.abc import Iterator
from pathlib import Path
from typing import IO
from unittest.mock import patch

images = importlib.import_module("tests.check_images")

_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "check_images"
_REGISTRY = "http://registry.invalid:5000"
_CONFIG_DIGEST = "sha256:2c8fe100e725000752c17caff6c303f2f1a7fd86b58e1e29e97cbb9e0666801d"
_MANIFEST_DIGEST = "sha256:d02720c42b21b0d9c5327ad6376442df5b9a5c454f617f38baf06317a9f0a116"


def _fixture(name: str) -> bytes:
    return (_FIXTURES / name).read_bytes()


def _config() -> dict[str, object]:
    config: dict[str, object] = json.loads(_fixture("config.json"))
    return config


class _Response(io.BytesIO):
    status = 200


def _registry(tags: set[str], config: bytes) -> contextlib.AbstractContextManager[object]:
    """Patch urlopen to serve the fixtures for rebrew/msvc:<tag> for each of *tags*."""
    bodies = {
        f"/v2/rebrew/msvc/manifests/{_MANIFEST_DIGEST}": _fixture("manifest.json"),
        f"/v2/rebrew/msvc/blobs/{_CONFIG_DIGEST}": config,
    }
    for tag in tags:
        bodies[f"/v2/rebrew/msvc/manifests/{tag}"] = _fixture("index.json")

    def urlopen(request: urllib.request.Request, timeout: float) -> _Response:
        del timeout
        url = request.full_url
        path = url.removeprefix(_REGISTRY)
        if path not in bodies:
            raise urllib.error.HTTPError(url, 404, "Not Found", email.message.Message(), None)
        return _Response(bodies[path])

    return patch.object(urllib.request, "urlopen", urlopen)


def _tree(files: dict[str, bytes]) -> bytes:
    """A tar like the engine's archive endpoint returns: one top directory."""
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as archive:
        for name, data in files.items():
            member = tarfile.TarInfo(f"bin/{name}")
            member.size = len(data)
            archive.addfile(member, io.BytesIO(data))
    return buffer.getvalue()


def _engine(
    histories: dict[str, list[str]], trees: dict[str, bytes]
) -> contextlib.AbstractContextManager[object]:
    """Patch the Engine API: image histories and each image's compiler directory."""
    containers: dict[str, str] = {}

    @contextlib.contextmanager
    def request(
        method: str, path: str, body: dict[str, object] | None = None
    ) -> Iterator[tuple[int, IO[bytes]]]:
        if method == "GET" and path.endswith("/history"):
            tag = path.removeprefix("/images/").removesuffix("/history")
            if tag not in histories:
                yield 404, io.BytesIO(b"{}")
                return
            steps = [{"CreatedBy": line} for line in reversed(histories[tag])]
            yield 200, io.BytesIO(json.dumps(steps).encode())
        elif method == "POST" and path == "/containers/create":
            if body is None:
                raise AssertionError("create without a body")
            container = f"c{len(containers)}"
            containers[container] = str(body["Image"])
            yield 201, io.BytesIO(json.dumps({"Id": container}).encode())
        elif method == "GET" and "/archive?" in path:
            tag = containers[path.split("/")[2]]
            yield (200, io.BytesIO(trees[tag])) if tag in trees else (404, io.BytesIO(b"{}"))
        elif method == "DELETE":
            del containers[path.split("/")[2].partition("?")[0]]
            yield 204, io.BytesIO(b"")
        else:
            raise AssertionError(f"unexpected engine call {method} {path}")

    return patch.object(images, "_engine", request)


class TestRecipePins(unittest.TestCase):
    def _run(self, argv: list[str]) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = images.main(argv)
        return code, out.getvalue()

    def test_a_tag_built_from_another_source_fails(self) -> None:
        with _registry({"7.0-win32"}, _fixture("config.json")):
            code, out = self._run(["--registry", _REGISTRY, "msvc-7.0"])
        self.assertEqual(code, 1)
        self.assertIn(
            "MISMATCH      msvc-7.0                       rebrew/msvc:7.0-win32: "
            "the recipe checked 13f86a2d618f, 618e876bc064; the catalogue pins 5f75462fb613",
            out,
        )

    def test_the_recipe_that_checked_the_pin_passes(self) -> None:
        # The same image is a correct build of msvc-7.1, which pins msvc710.
        with _registry({"7.1-win32"}, _fixture("config.json")):
            code, out = self._run(["--registry", _REGISTRY, "msvc-7.1"])
        self.assertEqual(code, 0, out)
        self.assertIn("ok            msvc-7.1", out)
        self.assertIn("compiler binaries: not compared", out)

    def test_a_recipe_that_checked_no_sum_fails(self) -> None:
        lines = images.history_of(_config())
        config = {"history": [{"created_by": by} for by in lines if "sha256sum" not in by]}
        with _registry({"7.1-win32"}, json.dumps(config).encode()):
            code, out = self._run(["--registry", _REGISTRY, "msvc-7.1"])
        self.assertEqual(code, 1)
        self.assertIn("NO-SUMS       msvc-7.1", out)

    def test_an_absent_image_is_reported_and_passes(self) -> None:
        with _registry(set(), _fixture("config.json")):
            code, out = self._run(["--registry", _REGISTRY, "msvc-7.0"])
        self.assertEqual(code, 0)
        self.assertIn("absent        msvc-7.0", out)
        self.assertIn("ok 0, MISMATCH 0, NO-SUMS 0, absent 1", out)

    def test_an_unknown_profile_is_refused_before_any_read(self) -> None:
        with (
            _registry(set(), b""),
            contextlib.redirect_stderr(io.StringIO()) as err,
        ):
            code, _out = self._run(["--registry", _REGISTRY, "msvc-7.0", "no-such"])
        self.assertEqual(code, 2)
        self.assertIn("no such profile: no-such", err.getvalue())

    def test_the_local_engine_history_is_read_the_same_way(self) -> None:
        history = images.history_of(_config())
        trees = {"rebrew/msvc:7.0-win32": _tree({"cl.exe": b"7.1"})}
        with _engine({"rebrew/msvc:7.0-win32": history}, trees):
            code, out = self._run(["msvc-7.0"])
        self.assertEqual(code, 1)
        self.assertIn("MISMATCH      msvc-7.0", out)


class TestDistinctCompilers(unittest.TestCase):
    def _run(self, trees: dict[str, bytes], profiles: list[str]) -> tuple[int, str]:
        catalogue = images.entries()
        histories = {
            catalogue[profile].tag: [
                f'RUN echo "{catalogue[profile].sha256}  /tmp/src.tar.gz" | sha256sum -c -'
            ]
            for profile in profiles
        }
        out = io.StringIO()
        with _engine(histories, trees), contextlib.redirect_stdout(out):
            code = images.main(profiles)
        return code, out.getvalue()

    def test_two_versions_with_one_compiler_fail(self) -> None:
        same = _tree({"cl.exe": b"13.10.3077", "c1.dll": b"c1", "c2.dll": b"c2"})
        code, out = self._run(
            {"rebrew/msvc:7.0-win32": same, "rebrew/msvc:7.1-win32": same},
            ["msvc-7.0", "msvc-7.1"],
        )
        self.assertEqual(code, 1)
        self.assertRegex(
            out,
            r"SAME-COMPILER msvc-7\.0 msvc-7\.1: identical binaries \([0-9a-f]{12}\) "
            r"claim msvc 7\.0; msvc 7\.1",
        )

    def test_a_shared_driver_with_other_passes_is_distinct(self) -> None:
        # 7.0 and 7.0 SP1 ship the same cl.exe; c1.dll and c2.dll differ.
        code, out = self._run(
            {
                "rebrew/msvc:7.0-win32": _tree({"cl.exe": b"cl", "c1.dll": b"rtm"}),
                "rebrew/msvc:7.0-sp1-win32": _tree({"cl.exe": b"cl", "c1.dll": b"sp1"}),
            },
            ["msvc-7.0", "msvc-7.0-sp1"],
        )
        self.assertEqual(code, 0, out)
        self.assertIn("compiler binaries, 2 images: 0 failing", out)

    def test_ids_of_one_claimed_version_print_as_alias(self) -> None:
        # A second id for one tree, and service packs that left cl/c1/c2 alone.
        same = _tree({"cl.exe": b"13.00.9466"})
        vc6 = _tree({"CL.EXE": b"12.00.8168"})
        code, out = self._run(
            {
                "rebrew/msvc:7.0-win32": same,
                "rebrew/msvc:7.0-rtm-win32": same,
                "rebrew/msvc:6.0-win32": vc6,
                "rebrew/msvc:6.0-sp1-win32": vc6,
            },
            ["msvc-7.0", "msvc-7.0-rtm", "msvc-6.0", "msvc-6.0-sp1"],
        )
        self.assertEqual(code, 0, out)
        self.assertIn("alias         msvc-7.0 msvc-7.0-rtm: identical binaries", out)
        self.assertIn("alias         msvc-6.0 msvc-6.0-sp1: identical binaries", out)

    def test_a_dosbox_compiler_is_compared_too(self) -> None:
        # The DOSBox recipes name no `binary`; their command runs C:\BIN\CL.EXE.
        # msvc-1.0 declares no shared compiler with msvc-1.5.
        same = _tree({"CL.EXE": b"8.00c", "C23216.EXE": b"c2"})
        code, out = self._run(
            {"rebrew/msvc:1.0-win16": same, "rebrew/msvc:1.5-win16": same},
            ["msvc-1.0", "msvc-1.5"],
        )
        self.assertEqual(code, 1)
        self.assertIn("SAME-COMPILER msvc-1.0 msvc-1.5", out)
        self.assertNotIn("unchecked", out)

    def test_a_declared_shared_compiler_passes(self) -> None:
        # sources.json: msvc-1.52 same_compiler_as msvc-1.5.
        same = _tree({"CL.EXE": b"8.00c", "C23216.EXE": b"c2"})
        code, out = self._run(
            {"rebrew/msvc:1.5-win16": same, "rebrew/msvc:1.52-win16": same},
            ["msvc-1.5", "msvc-1.52"],
        )
        self.assertEqual(code, 0, out)
        self.assertIn("declared      msvc-1.52 msvc-1.5: identical binaries", out)
        self.assertNotIn("SAME-COMPILER", out)

    def test_a_declared_shared_compiler_with_other_binaries_fails(self) -> None:
        code, out = self._run(
            {
                "rebrew/msvc:1.5-win16": _tree({"CL.EXE": b"8.00c"}),
                "rebrew/msvc:1.52-win16": _tree({"CL.EXE": b"8.00d"}),
            },
            ["msvc-1.5", "msvc-1.52"],
        )
        self.assertEqual(code, 1)
        self.assertIn(
            "DIFFERENT     msvc-1.52 msvc-1.5: same_compiler_as is declared, "
            "but the binaries differ",
            out,
        )

    def test_a_declaration_without_the_other_image_is_unverified(self) -> None:
        code, out = self._run(
            {"rebrew/msvc:1.52-win16": _tree({"CL.EXE": b"8.00c"})}, ["msvc-1.52"]
        )
        self.assertEqual(code, 0, out)
        self.assertIn("unverified    msvc-1.52", out)

    def test_an_image_without_its_compiler_directory_fails(self) -> None:
        code, out = self._run({}, ["msvc-7.0"])
        self.assertEqual(code, 1)
        self.assertIn(
            "NO-COMPILER   msvc-7.0                       rebrew/msvc:7.0-win32: "
            "no /opt/msvc7.0/Vc7/bin in the image",
            out,
        )


if __name__ == "__main__":
    unittest.main()
