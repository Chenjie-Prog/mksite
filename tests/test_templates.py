import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mksite.templates import render


class RenderTest(unittest.TestCase):
    def test_substitution(self):
        self.assertEqual(render("<h1>{{ title }}</h1>", {"title": "Hi"}),
                         "<h1>Hi</h1>")

    def test_missing_key_renders_empty(self):
        self.assertEqual(render("a {{ x }} b", {}), "a  b")

    def test_repeated_and_spaced(self):
        self.assertEqual(render("{{x}}{{ x }}", {"x": 1}), "11")

    def test_non_string_values(self):
        self.assertEqual(render("{{ n }}", {"n": 42}), "42")

    def test_ignores_other_braces(self):
        self.assertEqual(render("{ not a var }", {}), "{ not a var }")


if __name__ == "__main__":
    unittest.main()
