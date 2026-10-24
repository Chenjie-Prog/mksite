import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mksite.markdown import md_to_html


class HeadingTest(unittest.TestCase):
    def test_levels(self):
        for level in range(1, 7):
            hashes = "#" * level
            self.assertEqual(
                md_to_html("%s Title" % hashes),
                '<h%d id="title">Title</h%d>' % (level, level))

    def test_anchor_slug(self):
        self.assertEqual(md_to_html("# Hello, World! 你好"),
                         '<h1 id="hello-world-你好">Hello, World! 你好</h1>')

    def test_duplicate_slugs_get_suffix(self):
        html = md_to_html("# Same\n\n# Same")
        self.assertIn('id="same"', html)
        self.assertIn('id="same-2"', html)

    def test_no_space_is_not_heading(self):
        self.assertEqual(md_to_html("#tag"), "<p>#tag</p>")


class ParagraphTest(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(md_to_html("Hello world"), "<p>Hello world</p>")

    def test_consecutive_lines_join(self):
        self.assertEqual(md_to_html("line one\nline two"),
                         "<p>line one\nline two</p>")

    def test_blank_line_splits(self):
        self.assertEqual(md_to_html("a\n\nb"),
                         "<p>a</p>\n<p>b</p>")


class InlineTest(unittest.TestCase):
    def test_all_inline(self):
        html = md_to_html(
            "**b** *i* _i_ ~~s~~ `c` [x](http://e.com) ![alt](i.png)")
        self.assertEqual(
            html,
            "<p><strong>b</strong> <em>i</em> <em>i</em> <del>s</del> <code>c</code> "
            '<a href="http://e.com">x</a> <img src="i.png" alt="alt"></p>')

    def test_bold_inside_link(self):
        self.assertEqual(md_to_html("[**x**](http://e.com)"),
                         '<p><a href="http://e.com"><strong>x</strong></a></p>')

    def test_code_span_escapes_html(self):
        self.assertEqual(md_to_html("use `<b>` here"),
                         "<p>use <code>&lt;b&gt;</code> here</p>")

    def test_html_is_escaped(self):
        self.assertEqual(md_to_html("<script>alert(1)</script>"),
                         "<p>&lt;script&gt;alert(1)&lt;/script&gt;</p>")

    def test_intraword_underscore_not_italic(self):
        self.assertEqual(md_to_html("snake_case_name"),
                         "<p>snake_case_name</p>")

    def test_link_title(self):
        self.assertEqual(md_to_html('[x](http://e.com "T")'),
                         '<p><a href="http://e.com" title="T">x</a></p>')

    def test_image_alt_escaped(self):
        self.assertEqual(md_to_html('![a "b"](u.png)'),
                         '<p><img src="u.png" alt="a &quot;b&quot;"></p>')


class CodeFenceTest(unittest.TestCase):
    def test_with_language(self):
        self.assertEqual(md_to_html("```py\nprint(1)\n```"),
                         '<pre><code class="language-py">print(1)</code></pre>')

    def test_escapes_content(self):
        self.assertEqual(md_to_html("```\n<b>&\n```"),
                         "<pre><code>&lt;b&gt;&amp;</code></pre>")

    def test_unterminated_fence_runs_to_eof(self):
        self.assertEqual(md_to_html("```\nabc"),
                         "<pre><code>abc</code></pre>")

    def test_tilde_fence(self):
        self.assertEqual(md_to_html("~~~\nx\n~~~"),
                         "<pre><code>x</code></pre>")


class ListTest(unittest.TestCase):
    def test_unordered(self):
        self.assertEqual(md_to_html("- a\n- b"),
                         "<ul>\n<li>a</li>\n<li>b</li>\n</ul>")

    def test_ordered(self):
        self.assertEqual(md_to_html("1. a\n2. b"),
                         "<ol>\n<li>a</li>\n<li>b</li>\n</ol>")

    def test_ordered_start(self):
        self.assertEqual(md_to_html("3. a\n4. b"),
                         '<ol start="3">\n<li>a</li>\n<li>b</li>\n</ol>')

    def test_nested(self):
        self.assertEqual(
            md_to_html("- a\n  - b\n- c"),
            "<ul>\n<li>a\n<ul>\n<li>b</li>\n</ul></li>\n<li>c</li>\n</ul>")

    def test_inline_markdown_in_items(self):
        self.assertEqual(md_to_html("- **a**"),
                         "<ul>\n<li><strong>a</strong></li>\n</ul>")


class QuoteTest(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(md_to_html("> quoted"),
                         "<blockquote>\n<p>quoted</p>\n</blockquote>")

    def test_nested(self):
        self.assertEqual(md_to_html("> > deep"),
                         "<blockquote>\n<blockquote>\n<p>deep</p>\n"
                         "</blockquote>\n</blockquote>")


class TableTest(unittest.TestCase):
    def test_alignment(self):
        html = md_to_html("| L | C | R | N |\n| :-- | :-: | --: | --- |\n"
                          "| 1 | 2 | 3 | 4 |")
        self.assertIn("<table>", html)
        self.assertIn('<th style="text-align:left">L</th>', html)
        self.assertIn('<th style="text-align:center">C</th>', html)
        self.assertIn('<th style="text-align:right">R</th>', html)
        self.assertIn("<th>N</th>", html)
        self.assertIn('<td style="text-align:right">3</td>', html)

    def test_pipe_without_separator_is_paragraph(self):
        self.assertEqual(md_to_html("a | b\nstill text"),
                         "<p>a | b\nstill text</p>")


class MiscTest(unittest.TestCase):
    def test_horizontal_rule(self):
        self.assertEqual(md_to_html("---"), "<hr>")
        self.assertEqual(md_to_html("***"), "<hr>")

    def test_mixed_document(self):
        html = md_to_html("# T\n\ntext\n\n- item\n\n```\ncode\n```\n")
        self.assertIn("<h1", html)
        self.assertIn("<p>text</p>", html)
        self.assertIn("<li>item</li>", html)
        self.assertIn("<pre><code>code</code></pre>", html)

    def test_empty(self):
        self.assertEqual(md_to_html(""), "")


if __name__ == "__main__":
    unittest.main()
