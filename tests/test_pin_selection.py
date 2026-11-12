"""A mistyped pin-check selection must not report an empty successful check."""

from __future__ import annotations

import importlib
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from unittest.mock import patch

import catalog

pins = importlib.import_module("tests.check_pins")


class TestPinSelection(unittest.TestCase):
    def test_unknown_selection_is_rejected_before_network(self) -> None:
        for wanted in (["missing"], ["known", "missing"]):
            with (
                self.subTest(wanted=wanted),
                patch.object(catalog, "manifest", return_value={"known": {}}),
                patch.object(pins, "base_pins", return_value=[]),
                patch.object(pins, "check", return_value=None) as check,
                redirect_stdout(StringIO()),
                redirect_stderr(StringIO()) as error,
            ):
                self.assertEqual(pins.main(wanted), 2)
                self.assertIn("missing", error.getvalue())
                check.assert_not_called()

    def test_profile_and_base_selections_are_checked(self) -> None:
        url = "https://example.invalid/archive"
        for wanted in ("known", "base"):
            with (
                self.subTest(wanted=wanted),
                patch.object(catalog, "manifest", return_value={"known": {"url": url}}),
                patch.object(pins, "base_pins", return_value=[("base", url)]),
                patch.object(pins, "check", return_value=None) as check,
                redirect_stdout(StringIO()),
            ):
                self.assertEqual(pins.main([wanted]), 0)
                check.assert_called_once_with(url)
