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
