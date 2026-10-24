"""The builder visits only selected images' base dependencies."""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]


class TestBuildSelection(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
