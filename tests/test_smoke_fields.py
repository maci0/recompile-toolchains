"""tests/manifest_field.sh reads sources.json line by line for tests/smoke.sh.

A wrong read sends smoke to the wrong image tag (`host_dir`), the wrong
invocation (`arg_style`) or the wrong seccomp choice (`runner`), so every
profile's value is compared with a JSON parse of the same file.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
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


class TestSmoke(unittest.TestCase):
    def run_smoke(self, profile: str) -> tuple[str, list[str]]:
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            docker = work / "docker"
            docker.write_text(
                """#!/bin/sh
printf '%s\n' "$*" >> "$DOCKER_LOG"
[ "$1" = run ] || exit 0
while [ "$#" -gt 0 ]; do
    case "$1" in
        --entrypoint) exit 124 ;;
        -v)
            mount="${2%:/work}"
            printf 'fixture\n' > "$mount/t.o"
            printf 'fixture\n' > "$mount/t.obj"
            exit ;;
    esac
    shift
done
"""
            )
            magic = work / "file"
            magic.write_text("#!/bin/sh\necho COFF\n")
            docker.chmod(0o755)
            magic.chmod(0o755)
            log = work / "docker.log"
            result = subprocess.run(  # noqa: S603 - real smoke command with fixture Docker
                ["sh", "tests/smoke.sh", profile],  # noqa: S607
                cwd=_REPO,
                env=dict(
                    os.environ,
                    PATH=f"{work}:{os.environ['PATH']}",
                    PREFIX="fixture",
                    DOCKER_LOG=str(log),
                ),
                capture_output=True,
                text=True,
                check=False,
                timeout=_TIMEOUT_SECONDS,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            return result.stdout, log.read_text().splitlines() if log.exists() else []

    def test_smoke_runs_and_probes_the_tag_it_builds(self) -> None:
        _, calls = self.run_smoke("msvc-6.0-sp6")
        tag = "fixture/msvc:6.0-sp6-win32"
        self.assertTrue(any(f"-t {tag} " in call for call in calls), calls)
        self.assertEqual(len([call for call in calls if call.startswith("run ")]), 2, calls)
        for call in calls:
            if call.startswith("run "):
                self.assertIn(f" {tag} ", call)


if __name__ == "__main__":
    unittest.main()
