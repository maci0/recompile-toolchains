"""The committed ``toolchains.json`` must match the manifest.

The artifact is the catalogue consumers (rebrew, recompile, the Go backend and
compiler-detector) read instead of keeping a copy of ``sources.json``.  A
hand edit would silently split the catalogue again, so the test compares the
committed file with the renderer byte for byte and checks the consumer fields
every reader depends on.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import catalog
import toolchains

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_RUNTIME = frozenset({"exec", "wine", "wibo", "dosbox", "dosemu2", "daze"})
_FLAGS = frozenset({"msvc", "posix"})
_ARGS = frozenset({"msvc", "posix", "pipeline", "dos", "borland", "watcom"})


class TestToolchainsArtifact(unittest.TestCase):
    def test_committed_artifact_is_current(self) -> None:
        expected = toolchains.dump(toolchains.render(catalog.manifest()))
        actual = toolchains.ARTIFACT.read_text(encoding="utf-8")
        self.assertEqual(actual, expected, "run `make docs` to regenerate toolchains.json")

    def test_published_checksum_names_the_committed_artifact(self) -> None:
        # The digest a consumer pins sits at a stable path beside the
        # artifact, in `sha256sum -c` form, so nobody computes it by hand.
        digest = hashlib.sha256(toolchains.ARTIFACT.read_bytes()).hexdigest()
        self.assertEqual(
            toolchains.CHECKSUM.read_text(encoding="utf-8"),
            f"{digest}  toolchains.json\n",
            "run `make docs` to regenerate toolchains.json.sha256",
        )

    def test_check_refuses_a_stale_checksum(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stale = Path(tmp) / "toolchains.json.sha256"
            stale.write_text(f"{'0' * 64}  toolchains.json\n", encoding="utf-8")
            err = io.StringIO()
            with (
                mock.patch.object(toolchains, "CHECKSUM", stale),
                contextlib.redirect_stderr(err),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(toolchains.main(["--check"]), 1)
        self.assertIn("stale: toolchains.json.sha256", err.getvalue())

    def test_write_publishes_the_checksum(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp) / "toolchains.json"
            checksum = Path(tmp) / "toolchains.json.sha256"
            with (
                mock.patch.object(toolchains, "ARTIFACT", artifact),
                mock.patch.object(toolchains, "CHECKSUM", checksum),
                mock.patch.object(toolchains, "REPO", Path(tmp)),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(toolchains.main([]), 0)
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            self.assertEqual(checksum.read_text(encoding="utf-8"), f"{digest}  toolchains.json\n")

    def test_artifact_has_every_manifest_profile(self) -> None:
        data = json.loads(toolchains.ARTIFACT.read_text(encoding="utf-8"))
        manifest = catalog.manifest()
        self.assertEqual(data["schema_version"], toolchains.SCHEMA_VERSION)
        self.assertEqual(data["count"], len(manifest))
        self.assertEqual({row["id"] for row in data["toolchains"]}, set(manifest))

    def test_every_row_carries_the_consumer_contract(self) -> None:
        data = json.loads(toolchains.ARTIFACT.read_text(encoding="utf-8"))
        for row in data["toolchains"]:
            with self.subTest(profile=row["id"]):
                self.assertTrue(row["family"])
                self.assertTrue(row["platform"])
                self.assertIn(row["runtime"], _RUNTIME)
                self.assertTrue(row["entrypoint"])
                self.assertTrue(row["image_entrypoint"].startswith("/usr/local/bin/"))
                self.assertTrue(row["image"]["tag"].startswith("rebrew/"))
                self.assertRegex(row["source"]["sha256"], _SHA256)
                self.assertTrue(row["source"]["url"])
                consumer = row["consumer"]
                self.assertIn(consumer["flags_style"], _FLAGS)
                self.assertIn(consumer["arg_style"], _ARGS)
                self.assertTrue(consumer["obj_ext"].startswith("."))
                self.assertEqual("bits" in row, "arch" in row)

    def test_bits_agree_with_the_architecture(self) -> None:
        # A row's `bits` is the code model of its `arch`; `aarch64` with 32 bits
        # (the Switch clang rows) or `x86_16` with 32 (DJGPP) contradicts itself.
        width = {"x86_16": 16, "x86": 32, "x86_64": 64, "aarch64": 64, "mos6502": 8}
        data = json.loads(toolchains.ARTIFACT.read_text(encoding="utf-8"))
        for row in data["toolchains"]:
            if row.get("arch") in width:
                self.assertEqual(row["bits"], width[row["arch"]], row["id"])

    def test_a_withdrawn_entry_is_published_with_its_reason(self) -> None:
        # The row stays (stored records name the id); `withdrawn` tells a
        # consumer not to offer it, in the words build.sh refuses with.
        data = json.loads(toolchains.ARTIFACT.read_text(encoding="utf-8"))
        rows = {row["id"]: row for row in data["toolchains"]}
        self.assertIn("targets Itanium", rows["msvc-9.0-sp1"]["withdrawn"])
        self.assertEqual(
            {row["id"] for row in data["toolchains"] if "withdrawn" in row}, {"msvc-9.0-sp1"}
        )

    def test_aliases_resolve_to_one_profile(self) -> None:
        data = json.loads(toolchains.ARTIFACT.read_text(encoding="utf-8"))
        owner: dict[str, str] = {}
        profiles = {row["id"] for row in data["toolchains"]}
        for row in data["toolchains"]:
            for alias in row["aliases"]:
                self.assertNotIn(alias, profiles)
                self.assertEqual(owner.setdefault(alias, row["id"]), row["id"])

    def test_versions_and_service_packs_come_from_the_id(self) -> None:
        data = json.loads(toolchains.ARTIFACT.read_text(encoding="utf-8"))
        for row in data["toolchains"]:
            if row["version"]:
                self.assertIn(row["version"], row["id"])
            if "service_pack" in row:
                self.assertIn(row["service_pack"], row["id"])


if __name__ == "__main__":
    unittest.main()
