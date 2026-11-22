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
    histories: dict[str, list[str]],
    trees: dict[str, bytes],
    objects: dict[str, bytes] | None = None,
) -> contextlib.AbstractContextManager[object]:
    """Patch the Engine API: image histories, compiler directories, compiled objects.

    Starting a container of a tag in *objects* writes that object into the
    directory bound at /work, as the image's compiler would.
    """
    containers: dict[str, str] = {}
    binds: dict[str, str] = {}

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
            host = body.get("HostConfig")
            if isinstance(host, dict):
                binds[container] = str(host["Binds"][0]).partition(":")[0]
            yield 201, io.BytesIO(json.dumps({"Id": container}).encode())
        elif method == "POST" and path.endswith("/start"):
            container = path.split("/")[2]
            data = (objects or {}).get(containers[container])
            if data is not None:
                (Path(binds[container]) / "t.obj").write_bytes(data)
            yield 204, io.BytesIO(b"")
        elif method == "POST" and path.endswith("/wait"):
            yield 200, io.BytesIO(b'{"StatusCode": 0}')
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
            "the recipe checked 13f86a2d618f, 618e876bc064; the catalogue pins e8de76827817",
            out,
        )

    def test_the_recipe_that_checked_the_pin_passes(self) -> None:
        # The same recipe run against msvc-7.1's pin of today: msvc710 at its commit.
        sums = images.recipe_sums(images.history_of(_config()))
        branch = next(s for s in sums if s.startswith("618e876bc064"))
        config = _fixture("config.json").decode()
        rebuilt = config.replace(branch, images.entries()["msvc-7.1"].sums["primary"]).encode()
        with _registry({"7.1-win32"}, rebuilt):
            code, out = self._run(["--registry", _REGISTRY, "msvc-7.1"])
        self.assertEqual(code, 0, out)
        self.assertIn("ok            msvc-7.1", out)
        self.assertIn("compiler binaries: not compared (a registry serves layers", out)

    def test_a_build_from_the_replaced_branch_archive_passes(self) -> None:
        # The image is a build of msvc-7.1 from the branch archive of msvc710,
        # pinned until msvc-7.1 moved to the commit archive: same tree, other
        # bytes, both sums recorded in tools/migrate/commit-archives.json.
        with _registry({"7.1-win32"}, _fixture("config.json")):
            code, out = self._run(["--registry", _REGISTRY, "msvc-7.1"])
        self.assertEqual(code, 0, out)
        self.assertIn(
            "ok (branch)   msvc-7.1                       rebrew/msvc:7.1-win32: built from "
            "the branch archive its commit archive replaced (618e876bc064)",
            out,
        )
        self.assertIn("ok 0, ok (branch) 1, MISMATCH 0", out)

    def test_a_branch_archive_without_a_recorded_replacement_fails(self) -> None:
        # The same build with no row in commit-archives.json gets no allowance.
        with (
            patch.object(images, "COMMIT_ARCHIVES", _FIXTURES / "no-commit-archives.json"),
            _registry({"7.1-win32"}, _fixture("config.json")),
        ):
            code, out = self._run(["--registry", _REGISTRY, "msvc-7.1"])
        self.assertEqual(code, 1, out)
        self.assertIn("MISMATCH      msvc-7.1", out)

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
        self.assertIn("ok 0, ok (branch) 0, MISMATCH 0, NO-SUMS 0, absent 1", out)

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


def _coff(machine: int) -> bytes:
    return machine.to_bytes(2, "little") + bytes(18)


def _elf(machine: int, elf_class: int) -> bytes:
    return b"\x7fELF" + bytes([elf_class, 1]) + bytes(12) + machine.to_bytes(2, "little")


def _omf(segment_attributes: int) -> bytes:
    """THEADR, then a SEGDEF whose attribute byte's P bit says USE32."""
    return bytes([0x80, 2, 0, 0, 0]) + bytes([0x98, 7, 0, segment_attributes]) + bytes(6)


def _mz(header: bytes) -> bytes:
    """An MZ stub whose e_lfanew points at *header* (NE, or PE with its machine)."""
    return b"MZ" + bytes(0x3A) + (0x40).to_bytes(4, "little") + header + bytes(64)


def _asxxxx(header: str, port: str) -> bytes:
    """The first lines of an sdcc `.rel` (ASxxxx), with the `O` line sdcc writes."""
    return f"{header}\nH 9 areas 3 global symbols\nM t\nO -m{port}\nS .__.ABS. Def000000\n".encode()


#: One object per (arch, bits) pair toolchains.json carries, in each format a
#: compiler under such a row writes with its default invocation.  The byte
#: strings that are not built here are the first bytes of each image's smoke
#: object (docs/toolchain-qualification-2026-10-25.json, `magic`).
_PROBES: dict[tuple[str, int], dict[str, bytes]] = {
    ("aarch64", 64): {"ELF64 AArch64": _elf(183, 2)},
    ("arm", 32): {"ELF32 ARM": _elf(40, 1)},
    ("m68k", 32): {
        "ELF32 m68k": _elf(4, 1),
        "Amiga hunk (vbcc)": bytes.fromhex("000003e700000001742e6300000003e8"),
    },
    ("mcs51", 8): {"ASxxxx (sdcc 8051)": _asxxxx("XH3", "mcs51 --model-small")},
    ("mips", 32): {"ELF32 MIPS": _elf(8, 1)},
    ("mos6502", 8): {
        "ELF32 MOS (llvm-mos)": _elf(6502, 1),
        "xo65 (cc65)": bytes.fromhex("557a6e6111000000600000000b000000"),
    },
    ("powerpc", 32): {
        "ELF32 PowerPC": _elf(20, 1),
        "COFF PowerPC big-endian (Xbox 360)": bytes.fromhex("f20103007aebdc6a5c01000008000000")
        + bytes(4),
    },
    ("sh2", 32): {"ELF32 SH": _elf(42, 1)},
    ("sh4", 32): {"ELF32 SH": _elf(42, 1)},
    ("sm83", 8): {"ASxxxx (sdcc sm83)": _asxxxx("XL4", "sm83")},
    ("stm8", 8): {"ASxxxx (sdcc stm8)": _asxxxx("XH3", "stm8")},
    ("x86_16", 16): {
        "OMF USE16": _omf(0x48),
        "NE executable": _mz(b"NE"),
        "ELF32 i386 (ia16-elf)": _elf(3, 1),
    },
    ("x86", 32): {
        "COFF i386": _coff(0x014C),
        "OMF USE32": _omf(0xA9),
        "PE i386": _mz(b"PE\0\0" + (0x014C).to_bytes(2, "little")),
        "ELF32 i386": _elf(3, 1),
    },
    ("x86_64", 64): {"ELF64 x86-64": _elf(62, 2), "COFF x86-64": _coff(0x8664)},
    ("z80", 8): {
        "ASxxxx (sdcc z80)": _asxxxx("XL4", "z80"),
        "Z80RMF (z88dk)": bytes.fromhex("5a3830524d4631380100000000000000"),
    },
}
#: The one format that names no code width: ia16-elf writes its 16-bit code as
#: ELF32 i386, so an ELF i386 object agrees with an x86 and an x86_16 row.
#: ELF SH names no core either, so it agrees with sh2 and sh4.
_AMBIGUOUS = {"ELF32 i386 (ia16-elf)", "ELF32 i386", "ELF32 SH"}


def _one_profile_per_target() -> dict[tuple[str, int], str]:
    """The first offered profile of each (arch, bits) pair the catalogue carries."""
    catalogue = images.entries()
    by_target: dict[tuple[str, int], str] = {}
    for profile in sorted(catalogue):
        entry = catalogue[profile]
        if not entry.withdrawn:
            by_target.setdefault(entry.target, profile)
    return by_target


class TestObjectTargets(unittest.TestCase):
    def _run(self, objects: dict[str, bytes], profiles: list[str]) -> tuple[int, str]:
        catalogue = images.entries()
        histories = {
            catalogue[p].tag: [
                f'RUN echo "{sha}  /tmp/src.tar.gz" | sha256sum -c -'
                for sha in catalogue[p].sums.values()
            ]
            for p in profiles
        }
        trees = {catalogue[p].tag: _tree({p: p.encode()}) for p in profiles}
        out = io.StringIO()
        with _engine(histories, trees, objects), contextlib.redirect_stdout(out):
            code = images.main(profiles)
        return code, out.getvalue()

    def test_an_object_for_another_architecture_fails(self) -> None:
        # msvc-9.0-sp1's compiler wrote IA-64 COFF under an x86 row.
        code, out = self._run({"rebrew/msvc:9.0-win32": _coff(0x0200)}, ["msvc-9.0"])
        self.assertEqual(code, 1, out)
        self.assertIn(
            "WRONG-TARGET  msvc-9.0                       COFF machine 0x0200 (ia64 64), "
            "the row says x86 32",
            out,
        )

    def test_an_object_for_the_row_architecture_passes(self) -> None:
        code, out = self._run(
            {
                "rebrew/msvc:9.0-win32": _coff(0x014C),
                "rebrew/clang:9.0.0-switch": _elf(183, 2),
            },
            ["msvc-9.0", "clang-9.0.0"],
        )
        self.assertEqual(code, 0, out)
        self.assertIn("agree 2, WRONG-TARGET 0", out)

    def test_an_x86_64_object_under_an_aarch64_row_fails(self) -> None:
        # The Switch clang images wrote x86-64 ELF64 before their wrapper chose AArch64.
        code, out = self._run({"rebrew/clang:9.0.0-switch": _elf(62, 2)}, ["clang-9.0.0"])
        self.assertEqual(code, 1, out)
        self.assertIn("WRONG-TARGET  clang-9.0.0", out)

    def test_a_withdrawn_row_reports_and_passes(self) -> None:
        code, out = self._run({"rebrew/msvc:9.0-sp1-win32": _coff(0x0200)}, ["msvc-9.0-sp1"])
        self.assertEqual(code, 0, out)
        self.assertIn("withdrawn     msvc-9.0-sp1", out)

    def test_no_object_is_reported_and_passes(self) -> None:
        code, out = self._run({}, ["msvc-9.0"])
        self.assertEqual(code, 0, out)
        self.assertIn("no-object     msvc-9.0                       /c t.c wrote no object", out)
        self.assertIn("not checked 1 (no-object 1, unidentified 0)", out)

    def test_an_unreadable_object_is_counted_as_not_checked(self) -> None:
        # ACK writes its own object format, which names no machine.
        ack = bytes.fromhex("0202000000000400000005000d000000")
        code, out = self._run(
            {"rebrew/ack:6.2-7afa32a-linux386": ack}, ["ack-6.2-7afa32a-linux386"]
        )
        self.assertEqual(code, 0, out)
        self.assertIn("unidentified  ack-6.2-7afa32a-linux386", out)
        self.assertIn(
            "object targets, 1 images: agree 0, WRONG-TARGET 0, withdrawn 0, "
            "not checked 1 (no-object 0, unidentified 1)",
            out,
        )

    def test_the_rows_that_once_had_no_target_are_compiled_and_checked(self) -> None:
        # Apple GCC assembles with powerpc-linux-gnu-as; IDO writes MIPS ELF.
        code, out = self._run(
            {
                "rebrew/gcc:4.0.1-5363-macos": _elf(20, 1),
                "rebrew/ido:7.1-linux": _elf(8, 1),
                "rebrew/bootlin:m68k-glibc-2026.08-1-linux": _elf(8, 1),
            },
            ["gcc-4.0.1-5363", "ido-7.1-linux", "bootlin-m68k-glibc-2026.08-1"],
        )
        self.assertEqual(code, 1, out)
        self.assertIn("target        gcc-4.0.1-5363", out)
        self.assertIn("target        ido-7.1-linux", out)
        self.assertIn("WRONG-TARGET  bootlin-m68k-glibc-2026.08-1", out)
        self.assertIn("object targets, 3 images: agree 2, WRONG-TARGET 1", out)

    def test_a_32_bit_object_under_a_16_bit_row_fails(self) -> None:
        # A Win16 tag holding a 32-bit compiler: COFF i386, USE32 OMF or a PE.
        for name in ("COFF i386", "OMF USE32", "PE i386"):
            with self.subTest(name):
                code, out = self._run(
                    {"rebrew/msvc:1.52-win16": _PROBES["x86", 32][name]}, ["msvc-1.52"]
                )
                self.assertEqual(code, 1, out)
                self.assertRegex(
                    out, r"WRONG-TARGET  msvc-1\.52 .*\(x86 32\), the row says x86_16 16"
                )

    def test_a_16_bit_object_under_a_32_bit_row_fails(self) -> None:
        for name in ("OMF USE16", "NE executable"):
            with self.subTest(name):
                code, out = self._run(
                    {"rebrew/msvc:6.0-win32": _PROBES["x86_16", 16][name]}, ["msvc-6.0"]
                )
                self.assertEqual(code, 1, out)
                self.assertRegex(
                    out, r"WRONG-TARGET  msvc-6\.0 .*\(x86_16 16\), the row says x86 32"
                )

    def test_an_ia16_elf_object_under_the_ia16_row_passes(self) -> None:
        code, out = self._run(
            {"rebrew/ia16:6.3.0-20260612-msdos": _elf(3, 1)}, ["ia16-gcc-6.3.0-20260612"]
        )
        self.assertEqual(code, 0, out)
        self.assertIn("agree 1, WRONG-TARGET 0", out)

    def test_every_arch_and_bits_pair_has_a_probe_that_agrees(self) -> None:
        catalogue = images.entries()
        by_target = _one_profile_per_target()
        self.assertEqual(set(by_target), set(_PROBES), "a pair without a probe, or a stale probe")
        for target, probes in sorted(_PROBES.items()):
            profile = by_target[target]
            for name, data in probes.items():
                with self.subTest(target=target, probe=name):
                    code, out = self._run({catalogue[profile].tag: data}, [profile])
                    self.assertEqual(code, 0, out)
                    self.assertIn("agree 1, WRONG-TARGET 0", out)

    def test_every_probe_fails_under_every_other_pair(self) -> None:
        catalogue = images.entries()
        by_target = _one_profile_per_target()
        for target, probes in sorted(_PROBES.items()):
            for name, data in probes.items():
                if name in _AMBIGUOUS:
                    continue
                for other in sorted(set(_PROBES) - {target}):
                    with self.subTest(probe=name, row=other):
                        profile = by_target[other]
                        code, out = self._run({catalogue[profile].tag: data}, [profile])
                        self.assertEqual(code, 1, out)
                        self.assertIn(f"WRONG-TARGET  {profile}", out)

    def test_the_ambiguous_formats_fail_outside_their_pairs(self) -> None:
        catalogue = images.entries()
        rows = {"x86_64": "gcc-14.2.0", "sh2": "shc-5.0r32-sh2", "x86": "msvc-6.0"}
        for data, profile in (
            (_elf(3, 1), rows["x86_64"]),
            (_elf(42, 1), rows["x86"]),
            (_elf(3, 1), rows["sh2"]),
        ):
            with self.subTest(profile=profile):
                code, out = self._run({catalogue[profile].tag: data}, [profile])
                self.assertEqual(code, 1, out)
                self.assertIn(f"WRONG-TARGET  {profile}", out)

    def test_an_asxxxx_object_is_read_by_its_sdcc_port(self) -> None:
        catalogue = images.entries()
        tag = catalogue["sdcc-4.6.0-z80"].tag
        code, out = self._run({tag: _asxxxx("XL4", "sm83")}, ["sdcc-4.6.0-z80"])
        self.assertEqual(code, 1, out)
        self.assertIn("ASxxxx, sdcc port sm83 (sm83 8), the row says z80 8", out)

    def test_omf_code_width_is_read_from_the_first_segdef(self) -> None:
        self.assertEqual(
            images.object_target(_omf(0x48)),
            (frozenset({("x86_16", 16)}), "OMF, USE16 code segment"),
        )
        self.assertEqual(
            images.object_target(_omf(0xA9)), (frozenset({("x86", 32)}), "OMF, USE32 code segment")
        )


class TestDistinctCompilers(unittest.TestCase):
    def _run(self, trees: dict[str, bytes], profiles: list[str]) -> tuple[int, str]:
        catalogue = images.entries()
        histories = {
            catalogue[profile].tag: [
                f'RUN echo "{sha}  /tmp/src.tar.gz" | sha256sum -c -'
                for sha in catalogue[profile].sums.values()
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
            r"SAME-COMPILER msvc-7\.0 msvc-7\.1: identical binaries \([0-9a-f]{12}\), "
            r"no same_compiler_as ties msvc 7\.0 \(msvc-7\.0\); msvc 7\.1 \(msvc-7\.1\)",
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

    def test_two_service_packs_with_one_compiler_fail_undeclared(self) -> None:
        # Both claim 6.0: an SP4 tag holding the SP6 tree is the 7.0/7.1 mistake
        # one level down, and nothing but a declaration may excuse it.
        vc6 = _tree({"CL.EXE": b"12.00.8804", "C2.DLL": b"sp6"})
        code, out = self._run(
            {"rebrew/msvc:6.0-sp4-win32": vc6, "rebrew/msvc:6.0-sp6-win32": vc6},
            ["msvc-6.0-sp4", "msvc-6.0-sp6"],
        )
        self.assertEqual(code, 1)
        self.assertRegex(
            out,
            r"SAME-COMPILER msvc-6\.0-sp4 msvc-6\.0-sp6: identical binaries \([0-9a-f]{12}\), "
            r"no same_compiler_as ties msvc 6\.0 \(msvc-6\.0-sp4\); msvc 6\.0 \(msvc-6\.0-sp6\)",
        )

    def test_declared_service_packs_with_one_compiler_pass(self) -> None:
        # sources.json: msvc-6.0-sp1 and -sp2 same_compiler_as msvc-6.0.
        vc6 = _tree({"CL.EXE": b"12.00.8168"})
        code, out = self._run(
            {
                "rebrew/msvc:6.0-win32": vc6,
                "rebrew/msvc:6.0-sp1-win32": vc6,
                "rebrew/msvc:6.0-sp2-win32": vc6,
            },
            ["msvc-6.0", "msvc-6.0-sp1", "msvc-6.0-sp2"],
        )
        self.assertEqual(code, 0, out)
        self.assertIn("declared      msvc-6.0-sp1 msvc-6.0: identical binaries", out)
        self.assertIn("declared      msvc-6.0-sp2 msvc-6.0: identical binaries", out)

    def test_a_variant_shares_its_base_compiler(self) -> None:
        # watcom-11.0-cxx is variant_of watcom-11.0: the same tree, wpp386 beside wcc386.
        tree = _tree({"wcc386.exe": b"c", "wpp386.exe": b"c++"})
        code, out = self._run(
            {"rebrew/watcom:11.0-win32": tree, "rebrew/watcom:11.0-cxx-win32": tree},
            ["watcom-11.0", "watcom-11.0-cxx"],
        )
        self.assertEqual(code, 0, out)
        self.assertNotIn("SAME-COMPILER", out)

    def test_a_repinned_secondary_download_fails(self) -> None:
        # gcc-2.7.2-snew fetches its compiler and modern-asn64.py; the history
        # checks only the compiler's sum.
        catalogue = images.entries()
        entry = catalogue["gcc-2.7.2-snew"]
        history = [f'RUN echo "{entry.sums["primary"]}  /tmp/src.tar.gz" | sha256sum -c -']
        out = io.StringIO()
        with _engine({entry.tag: history}, {}), contextlib.redirect_stdout(out):
            code = images.recipe_pins(catalogue, ["gcc-2.7.2-snew"], "")[0]
        self.assertEqual(code, 1)
        self.assertIn(f"the catalogue pins extra0 {entry.sums['extra0'][:12]}", out.getvalue())

    def test_every_entry_names_its_compiler(self) -> None:
        unchecked = sorted(p for p, e in images.entries().items() if not e.compiler_dir)
        self.assertEqual(unchecked, [], "recipes without a compiler binary")

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
