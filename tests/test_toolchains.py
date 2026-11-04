"""The committed ``toolchains.json`` must match the manifest.

The artifact is the catalogue consumers (rebrew, recompile, the Go backend and
compiler-detector) read instead of keeping a copy of ``sources.json``.  A
hand edit would silently split the catalogue again, so the test compares the
committed file with the renderer byte for byte and checks the consumer fields
every reader depends on.
"""

from __future__ import annotations

import json
import re
import unittest

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
