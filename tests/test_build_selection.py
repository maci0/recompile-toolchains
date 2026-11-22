"""The builder visits only selected images' base dependencies."""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]


class TestBuildSelection(unittest.TestCase):
    def test_all_zero_build_limits_are_rejected_before_docker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            log = work / "calls"
            docker = work / "docker"
            docker.write_text('#!/bin/sh\necho called >> "$BUILD_CALLS"\n')
            docker.chmod(0o755)
            for knob in ("REBREW_BUILD_JOBS", "REBREW_BUILD_TIMEOUT"):
                for value in ("00", "000"):
                    with self.subTest(knob=knob, value=value):
                        log.unlink(missing_ok=True)
                        env = dict(
                            os.environ, PATH=f"{work}:{os.environ['PATH']}", BUILD_CALLS=str(log)
                        )
                        env[knob] = value
                        result = subprocess.run(  # noqa: S603  (tracked builder, stubbed docker)
                            [str(_REPO / "build.sh"), "gcc-14.2.0"],
                            env=env,
                            capture_output=True,
                            text=True,
                            timeout=60,
                            check=False,
                        )
                        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                        self.assertIn(f"{knob} must be a positive integer", result.stderr)
                        self.assertFalse(log.exists())

    def test_explicit_base_selection_builds_its_dependencies_once(self) -> None:
        cases = (
            ("base", ["base"]),
            ("base-noble", ["base", "base-noble"]),
            ("base-dosemu", ["base", "base-noble", "base-dosemu"]),
        )
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            docker = work / "docker"
            docker.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$BUILD_CALLS"\n')
            docker.chmod(0o755)
            log = work / "calls"
            env = dict(os.environ, PATH=f"{work}:{os.environ['PATH']}", BUILD_CALLS=str(log))
            env["PREFIX"] = "test-registry/team"
            for selected, bases in cases:
                with self.subTest(selected=selected):
                    log.unlink(missing_ok=True)
                    result = subprocess.run(  # noqa: S603  (tracked builder, stubbed docker)
                        [str(_REPO / "build.sh"), selected],
                        env=env,
                        capture_output=True,
                        text=True,
                        timeout=60,
                        check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    calls = [line.split() for line in log.read_text().splitlines()]
                    self.assertEqual([Path(call[-1]).name for call in calls], bases)
                    self.assertEqual(
                        [call[call.index("-t") + 1] for call in calls],
                        [f"test-registry/team/{base}:1.0" for base in bases],
                    )
                    self.assertTrue(
                        all("HELPER_IMAGE=test-registry/team/base:1.0" in call for call in calls)
                    )
                    self.assertTrue(
                        all(
                            "NOBLE_IMAGE=test-registry/team/base-noble:1.0" in call
                            for call in calls
                        )
                    )

    def test_base_dependency_selection(self) -> None:
        cases = (
            ("gcc-14.2.0", ["base"]),
            ("psyq-3.3-daze-0.3.0", ["base"]),
            ("ido-4.1", ["base", "base-noble"]),
            ("psyq-3.3", ["base", "base-noble", "base-dosemu"]),
        )
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            docker = work / "docker"
            docker.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$BUILD_CALLS"\n')
            docker.chmod(0o755)
            log = work / "calls"
            env = dict(os.environ, PATH=f"{work}:{os.environ['PATH']}", BUILD_CALLS=str(log))
            env["PREFIX"] = "test-registry/team"
            for profile, bases in cases:
                with self.subTest(profile=profile):
                    log.unlink(missing_ok=True)
                    result = subprocess.run(  # noqa: S603  (tracked script, fixed test cases)
                        [str(_REPO / "build.sh"), profile],
                        env=env,
                        capture_output=True,
                        text=True,
                        timeout=60,
                        check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    calls = log.read_text().splitlines()
                    contexts = [Path(line.split()[-1]) for line in calls]
                    self.assertEqual([p.name for p in contexts[:-1]], bases)
                    self.assertEqual(len(calls), len(bases) + 1)
                    self.assertTrue(all("-t test-registry/team/" in line for line in calls))

    def _run_stubbed(self, args: list[str]) -> tuple[subprocess.CompletedProcess[str], list[str]]:
        """build.sh with a docker stub that logs its calls; (result, calls)."""
        scratch = _REPO / ".scratch"
        scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            work = Path(directory)
            docker = work / "docker"
            docker.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$BUILD_CALLS"\n')
            docker.chmod(0o755)
            log = work / "calls"
            env = dict(os.environ, PATH=f"{work}:{os.environ['PATH']}", BUILD_CALLS=str(log))
            env["REBREW_BUILD_JOBS"] = "8"
            result = subprocess.run(  # noqa: S603  (tracked script, stubbed docker)
                [str(_REPO / "build.sh"), *args],
                env=env,
                capture_output=True,
                text=True,
                timeout=600,
                check=False,
            )
            calls = log.read_text().splitlines() if log.exists() else []
        return result, calls

    def test_a_withdrawn_profile_is_refused_with_its_reason(self) -> None:
        # msvc-9.0-sp1's compiler targets Itanium; sources.json withdraws it.
        for name in ("msvc-9.0-sp1", "msvc/9.0-sp1-win32"):
            with self.subTest(name=name):
                result, calls = self._run_stubbed([name])
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn(
                    "refusing to build: msvc-9.0-sp1 is withdrawn: its compiler targets Itanium",
                    result.stderr,
                )
                self.assertEqual(calls, [])

    def test_a_full_sweep_skips_a_withdrawn_profile(self) -> None:
        result, calls = self._run_stubbed([])
        self.assertEqual(result.returncode, 0, result.stdout[-2000:] + result.stderr[-2000:])
        self.assertIn("==> skipping: msvc-9.0-sp1 is withdrawn", result.stderr)
        self.assertFalse(any("msvc:9.0-sp1-win32" in call for call in calls))
        self.assertTrue(any("msvc:9.0-win32" in call for call in calls))


if __name__ == "__main__":
    unittest.main()
