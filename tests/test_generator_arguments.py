"""A misspelled check option must not fall through to generation."""

from __future__ import annotations

import unittest
from contextlib import redirect_stderr
from io import StringIO
from unittest.mock import patch

import catalog
import generate
import toolchains


class TestGeneratorArguments(unittest.TestCase):
    def test_unknown_options_are_rejected_before_loading_inputs(self) -> None:
        for module in (catalog, generate, toolchains):
            for arguments in (["--chekc"], ["--check", "--unexpected"]):
                with (
                    self.subTest(module=module.__name__, arguments=arguments),
                    patch.object(
                        catalog,
                        "manifest",
                        side_effect=AssertionError("invalid options reached manifest processing"),
                    ) as catalog_input,
                    patch.object(
                        generate,
                        "manifest",
                        side_effect=AssertionError("invalid options reached manifest processing"),
                    ) as generator_input,
                    redirect_stderr(StringIO()),
                ):
                    self.assertEqual(module.main(arguments), 2)
                    catalog_input.assert_not_called()
                    generator_input.assert_not_called()
