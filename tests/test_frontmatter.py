import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mksite.frontmatter import parse


class FrontmatterTest(unittest.TestCase):
    def test_no_frontmatter(self):
        meta, body = parse("just body")
        self.assertEqual(meta, {})
        self.assertEqual(body, "just body")

    def test_basic(self):
        meta, body = parse("---\ntitle: Hi\ndate: 2026-10-24\n---\n\nbody")
        self.assertEqual(meta["title"], "Hi")
        self.assertEqual(meta["date"], "2026-10-24")
        self.assertEqual(body, "\nbody")

    def test_types(self):
        meta, _ = parse("---\nn: 3\nf: 1.5\nb: true\ns: false\n---\n")
        self.assertEqual(meta["n"], 3)
        self.assertEqual(meta["f"], 1.5)
        self.assertIs(meta["b"], True)
        self.assertIs(meta["s"], False)

    def test_list(self):
        meta, _ = parse("---\ntags: [a, b]\nempty: []\n---\n")
        self.assertEqual(meta["tags"], ["a", "b"])
        self.assertEqual(meta["empty"], [])

    def test_quoted_string_keeps_commas(self):
        meta, _ = parse('---\ntitle: "Hello, world"\n---\n')
        self.assertEqual(meta["title"], "Hello, world")

    def test_unclosed_frontmatter_is_body(self):
        meta, body = parse("---\ntitle: Hi\n\nno closing fence")
        self.assertEqual(meta, {})
        self.assertTrue(body.startswith("---"))


if __name__ == "__main__":
    unittest.main()
