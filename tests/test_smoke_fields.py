"""tests/manifest_field.sh reads sources.json line by line for tests/smoke.sh.

A wrong read sends smoke to the wrong image tag (`host_dir`), the wrong
invocation (`arg_style`) or the wrong seccomp choice (`runner`), so every
profile's value is compared with a JSON parse of the same file.
"""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_SCRIPT = _REPO / "tests" / "manifest_field.sh"
#: A wedged awk must fail the test, not hang it.
_TIMEOUT_SECONDS = 30


def _field(profile: str, key: str) -> str:
    done = subprocess.run(  # noqa: S603 - fixed script, arguments from sources.json
        ["sh", str(_SCRIPT), profile, key],  # noqa: S607 - sh from PATH, as make runs it
        capture_output=True,
        text=True,
        check=True,
        timeout=_TIMEOUT_SECONDS,
    )
    return done.stdout.removesuffix("\n")


def _runner(entry: dict[str, object]) -> str:
    recipe = entry.get("recipe")
    if not isinstance(recipe, dict):
        return ""
    env = recipe.get("env")
    selected = env.get("REBREW_RUNNER") if isinstance(env, dict) else None
    return str(selected or recipe.get("runner", ""))


class TestManifestField(unittest.TestCase):
    def test_every_profile_reads_as_the_json_parse(self) -> None:
        manifest = json.loads((_REPO / "sources.json").read_text(encoding="utf-8"))
        for profile, entry in manifest.items():
            with self.subTest(profile=profile):
                self.assertEqual(_field(profile, "host_dir"), entry["host_dir"])
                self.assertEqual(_field(profile, "arg_style"), entry.get("arg_style", ""))
                self.assertEqual(_field(profile, "runner"), _runner(entry))

    def test_the_recipe_env_selects_the_runner(self) -> None:
        # psyq-4.0's recipe sets REBREW_RUNNER=wibo; psyq-4.6 runs the default wine.
        self.assertEqual(_field("psyq-4.0", "runner"), "wibo")
        self.assertEqual(_field("psyq-4.6", "runner"), "wine")

    def test_an_unknown_profile_or_field_reads_empty(self) -> None:
        self.assertEqual(_field("not-a-profile", "host_dir"), "")
        self.assertEqual(_field("msvc-6.0", "not-a-field"), "")
        # A field of a later entry is not read into an earlier one.
        self.assertEqual(_field("msvc-6.0", "withdrawn"), "")


if __name__ == "__main__":
    unittest.main()
