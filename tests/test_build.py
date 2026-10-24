import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mksite.build import build, load_config
from mksite.build import MksiteError

SITE = {
    "site.json": '{"name": "Test Site", "base_url": "https://example.com"}',
    "templates/page.html": "<html><title>{{ title }}</title>"
                           "<body>{{ content }}</body></html>",
    "static/style.css": "body{}",
    "content/index.md": "---\ntitle: Home\n---\n\n# Welcome\n\nhello",
    "content/about.md": "# About\n\nsome text",
    "content/posts/a.md": "---\ntitle: Post A\ndate: 2026-10-01\n---\n\n"
                          "# Post A\n\ncontent a",
    "content/posts/b.md": "---\ntitle: Post B\ndate: 2026-10-24\n---\n\n"
                          "# Post B\n\ncontent b",
    "content/img/pic.png": "fake-png",
}


def make_site(root):
    for rel, text in SITE.items():
        path = Path(root) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


class BuildTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.src = Path(self.tmp.name) / "site"
        make_site(self.src)
        self.result = build(self.src)

    def tearDown(self):
        self.tmp.cleanup()

    def out(self, *parts):
        return self.src / "public" / Path(*parts)

    def test_page_count(self):
        self.assertEqual(self.result["pages"], 4)

    def test_renders_markdown_pages(self):
        html = self.out("index.html").read_text(encoding="utf-8")
        self.assertIn("<h1", html)
        self.assertIn("Welcome", html)
        self.assertIn("<title>Home</title>", html)

    def test_nested_page_paths(self):
        self.assertTrue(self.out("posts", "a.html").exists())

    def test_static_files_copied(self):
        self.assertEqual(self.out("style.css").read_text(encoding="utf-8"), "body{}")

    def test_non_markdown_files_in_content_copied(self):
        self.assertEqual(self.out("img", "pic.png").read_text(encoding="utf-8"),
                         "fake-png")

    def test_feed_generated_and_sorted(self):
        feed = self.out("feed.xml").read_text(encoding="utf-8")
        self.assertIn("<rss", feed)
        self.assertIn("Post B", feed)
        self.assertLess(feed.index("Post B"), feed.index("Post A"))

    def test_sitemap_generated(self):
        sitemap = self.out("sitemap.xml").read_text(encoding="utf-8")
        self.assertIn("https://example.com/posts/a.html", sitemap)

    def test_title_from_first_heading_when_missing(self):
        html = self.out("about.html").read_text(encoding="utf-8")
        self.assertIn("<title>About</title>", html)


class MissingContentTest(unittest.TestCase):
    def test_error_when_no_content_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(MksiteError):
                build(tmp)


class IndexSynthesisTest(unittest.TestCase):
    def test_generated_index_lists_posts_by_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp)
            (src / "content" / "posts").mkdir(parents=True)
            (src / "content" / "posts" / "x.md").write_text(
                "---\ntitle: X\ndate: 2026-01-01\n---\n\nbody", encoding="utf-8")
            result = build(src)
            self.assertEqual(result["pages"], 2)
            html = (src / "public" / "index.html").read_text(encoding="utf-8")
            self.assertIn("X", html)
            self.assertIn("2026-01-01", html)


class ConfigTest(unittest.TestCase):
    def test_defaults_without_site_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = load_config(tmp)
            self.assertEqual(config["name"], "My Site")

    def test_bad_json_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "site.json").write_text("{oops", encoding="utf-8")
            with self.assertRaises(MksiteError):
                load_config(tmp)


if __name__ == "__main__":
    unittest.main()
