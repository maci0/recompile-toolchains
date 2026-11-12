"""Qualified migration repairs still reject an unreviewed recipe or wrapper edit."""

from __future__ import annotations

import hashlib
import importlib
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

migration = importlib.import_module("tools.migrate.verify_migration")


class TestMigration(unittest.TestCase):
    def test_archive_ownership_normalization_preserves_other_flags(self) -> None:
        clauses = migration.install_clauses
        self.assertEqual(clauses("RUN tar xzf input --no-same-owner"), clauses("RUN tar xzf input"))
        self.assertNotEqual(
            clauses("RUN tar xzf input --strip-components=1"), clauses("RUN tar xzf input")
        )

    def test_user_and_workdir_changes_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            old, new = root / "old", root / "new"
            old.mkdir()
            new.mkdir()
            for instruction, before, after, field in (
                ("USER", "builder", "root", "user"),
                ("WORKDIR", "/work", "/other", "workdir"),
            ):
                with self.subTest(instruction=instruction):
                    (old / "Dockerfile").write_text(f"FROM scratch\n{instruction} {before}\n")
                    (new / "Dockerfile").write_text(f"FROM scratch\n{instruction} {after}\n")
                    self.assertEqual(
                        migration.diff(old, new), [f"{field}: {before!r} -> {after!r}"]
                    )
                    (new / "Dockerfile").write_text("FROM scratch\n")
                    self.assertTrue(migration.diff(old, new))
                    self.assertEqual(migration.diff(old, old), [])

    def test_checksum_changes_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            old, new = Path(temporary) / "old", Path(temporary) / "new"
            old.mkdir()
            new.mkdir()
            check = f'RUN echo "{"a" * 64}  /tmp/compiler" | sha256sum -c -\n'
            (old / "Dockerfile").write_text(check)
            for changed in (check.replace("a" * 64, "b" * 64), check.split(" | ")[0], ""):
                with self.subTest(changed=changed):
                    (new / "Dockerfile").write_text(changed)
                    self.assertTrue(migration.clause_diff(old, new))

    def test_checksum_may_move_before_but_not_after_use(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            old, new = Path(temporary) / "old", Path(temporary) / "new"
            old.mkdir()
            new.mkdir()
            check = f'RUN echo "{"a" * 64}  /tmp/compiler" | sha256sum -c -\n'
            extract = "RUN tar xzf /tmp/compiler -C /opt/compiler\n"
            (old / "Dockerfile").write_text("RUN mkdir -p /opt/compiler\n" + check + extract)
            (new / "Dockerfile").write_text(check + "RUN mkdir -p /opt/compiler\n" + extract)
            self.assertEqual(migration.clause_diff(old, new), [])
            (new / "Dockerfile").write_text("RUN mkdir -p /opt/compiler\n" + extract + check)
            self.assertIn("checksum follows use: /tmp/compiler", migration.clause_diff(old, new))

    def test_qualified_repair_rejects_later_edits(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            old, new = root / "old" / "tool", root / "new" / "tool"
            for directory, compiler in [(old, "old"), (new, "fixed")]:
                directory.mkdir(parents=True)
                (directory / "Dockerfile").write_text(
                    'FROM scratch\nCOPY cc.sh /usr/local/bin/cc\nENTRYPOINT ["/usr/local/bin/cc"]\n'
                )
                (directory / "cc.sh").write_text(f'#!/bin/sh\nexec {compiler} "$@"\n')
            data = (new / "Dockerfile").read_bytes() + (new / "cc.sh").read_bytes()
            qualified = {"test": hashlib.sha256(data).hexdigest()}
            with (
                patch.object(migration, "REPO", new.parent),
                patch.object(migration, "checkout", return_value=old.parent),
                patch.object(migration, "discard"),
                patch.object(
                    migration.generate, "manifest", return_value={"test": {"host_dir": "tool"}}
                ),
                patch.object(migration, "QUALIFIED_REPAIRS", qualified),
                redirect_stdout(StringIO()),
            ):
                self.assertEqual(migration.main(["--baseline", "test"]), 0)
                (new / "cc.sh").write_text('#!/bin/sh\nexec unreviewed "$@"\n')
                self.assertEqual(migration.main(["--baseline", "test"]), 1)

    def test_a_mirror_url_reads_as_its_upstream(self) -> None:
        upstream = "https://upstream.example/cc.tar.gz"
        mirror = "https://github.com/archaic-toolchains/cc/releases/download/2026-11-10/cc.tar.gz"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            old, new = root / "old" / "tool", root / "new" / "tool"
            for directory, url in [(old, upstream), (new, mirror)]:
                directory.mkdir(parents=True)
                (directory / "Dockerfile").write_text(
                    f'FROM scratch\nRUN curl -fsSL -o /tmp/cc.tar.gz "{url}"\n'
                    'ENTRYPOINT ["/usr/local/bin/cc"]\n'
                )
            with (
                patch.object(migration, "REPO", new.parent),
                patch.object(migration, "checkout", return_value=old.parent),
                patch.object(migration, "discard"),
                patch.object(
                    migration.generate, "manifest", return_value={"test": {"host_dir": "tool"}}
                ),
                redirect_stdout(StringIO()),
            ):
                with patch.object(migration, "MIRRORS", {mirror: upstream}):
                    self.assertEqual(migration.main(["--baseline", "test"]), 0)
                with patch.object(migration, "MIRRORS", {}):
                    self.assertEqual(migration.main(["--baseline", "test"]), 1)
