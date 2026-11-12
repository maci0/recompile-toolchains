"""Dockerfile keyword separators do not alter argument bytes."""

import importlib
import unittest

migration = importlib.import_module("tools.migrate.verify_migration")


class TestInstructionWhitespace(unittest.TestCase):
    def test_tabs_separate_keywords_without_changing_quoted_spaces(self) -> None:
        self.assertEqual(migration.instructions("RuN\tprintf 'a  b'\n"), ["RUN printf 'a  b'"])
