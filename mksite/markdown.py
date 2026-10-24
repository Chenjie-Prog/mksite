"""A small, dependency-free Markdown -> HTML converter.

Supported syntax (a pragmatic GitHub-Flavoured-Markdown subset):

* ATX headings ``#`` .. ``######``, rendered with anchor ``id`` attributes
* paragraphs
* block quotes (nestable; content is parsed recursively)
* fenced code blocks (``` or ~~~) with an optional language tag
* unordered lists (``-``, ``*``, ``+``) and ordered lists (``1.`` / ``1.)``,
  with an ``start`` attribute when the first number is not 1), nestable
* pipe tables with per-column alignment (``:---``, ``:---:``, ``---:``)
* horizontal rules (``---``, ``***``, ``___``)
* inline: ``**bold**``, ``*italic*``, ``_italic_``, ``~~strike~~``,
  inline ```` ``code`` ````, ``[links](url)`` and ``![images](url)``

Not supported (by design, to keep the engine small): raw HTML pass-through
(all HTML is escaped), indented code blocks, setext headings, footnotes.
"""

import html
import re

__all__ = ["md_to_html"]

_FENCE_RE = re.compile(r"^(\s{0,3})(`{3,}|~{3,})(.*)$")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_HR_RE = re.compile(r"^ {0,3}(?:-[ \t]*){3,}$|^ {0,3}(?:\*[ \t]*){3,}$|^ {0,3}(?:_[ \t]*){3,}$")
_LIST_RE = re.compile(r"^(\s*)(?:([-*+])|(\d+)[.)])\s+(.*)$")
_QUOTE_RE = re.compile(r"^\s*>\s?(.*)$")
_TABLE_SEP_RE = re.compile(r"^\s*\|?[\s:|-]+\|?\s*$")

_CODESPAN_RE = re.compile(r"(`+)(.+?)\1", re.S)
_IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"([^\"]*)\")?\)")
_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)\s]+)(?:\s+\"([^\"]*)\")?\)")
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*|__(.+?)__", re.S)
_EM_RE = re.compile(r"\*([^*\n]+)\*|(?<![\w_])_([^_\n]+)_(?![\w_])")
_DEL_RE = re.compile(r"~~(.+?)~~", re.S)


def md_to_html(text):
    """Convert a Markdown document to an HTML string."""
    return _Parser(text.splitlines()).parse()


def _indent_width(line):
    return len(line) - len(line.lstrip(" "))


class _Parser:
    def __init__(self, lines):
        self.lines = lines
        self._slugs = {}

    def parse(self):
        out = []
        i = 0
        n = len(self.lines)
        while i < n:
            line = self.lines[i]
            if not line.strip():
                i += 1
                continue
            fence = _FENCE_RE.match(line)
            if fence:
                i = self._fence(fence, i, out)
                continue
            if _HR_RE.match(line):
                out.append("<hr>")
                i += 1
                continue
            heading = _HEADING_RE.match(line)
            if heading:
                level = len(heading.group(1))
                text = re.sub(r"\s+#+\s*$", "", heading.group(2).rstrip())
                out.append('<h%d id="%s">%s</h%d>'
                           % (level, self._slug(text), _inline(text), level))
                i += 1
                continue
            if _QUOTE_RE.match(line):
                i = self._quote(i, out)
                continue
            if _LIST_RE.match(line):
                i = self._list(i, out)
                continue
            if ("|" in line and i + 1 < n and "|" in self.lines[i + 1]
                    and "-" in self.lines[i + 1]
                    and _TABLE_SEP_RE.match(self.lines[i + 1])):
                i = self._table(i, out)
                continue
            i = self._paragraph(i, out)
        return "\n".join(out)

    # ---- block elements -------------------------------------------------

    def _fence(self, match, i, out):
        fence = match.group(2)
        lang = match.group(3).strip().split()[0] if match.group(3).strip() else ""
        i += 1
        buf = []
        while i < len(self.lines):
            stripped = self.lines[i].strip()
            if stripped and set(stripped) == {fence[0]} and len(stripped) >= len(fence):
                break
            buf.append(self.lines[i])
            i += 1
        i += 1  # skip the closing fence
        code = html.escape("\n".join(buf), quote=False)
        cls = ' class="language-%s"' % lang if lang else ""
        out.append("<pre><code%s>%s</code></pre>" % (cls, code))
        return i

    def _quote(self, i, out):
        buf = []
        while i < len(self.lines):
            m = _QUOTE_RE.match(self.lines[i])
            if not m:
                break
            buf.append(m.group(1))
            i += 1
        out.append("<blockquote>\n%s\n</blockquote>" % _Parser(buf).parse())
        return i

    def _list(self, i, out):
        first = _LIST_RE.match(self.lines[i])
        base = _indent_width(first.group(1))
        ordered = first.group(3) is not None
        start = int(first.group(3)) if ordered else 1
        items = []
        while i < len(self.lines):
            line = self.lines[i]
            if not line.strip():
                break
            m = _LIST_RE.match(line)
            if not m:
                break
            if _indent_width(m.group(1)) != base:
                break
            content = [m.group(4)]
            i += 1
            # attach deeper-indented lines (nested lists, extra paragraphs)
            while i < len(self.lines) and self.lines[i].strip():
                m2 = _LIST_RE.match(self.lines[i])
                indent = (_indent_width(m2.group(1)) if m2
                          else _indent_width(self.lines[i]))
                if indent > base:
                    content.append(self.lines[i])
                    i += 1
                else:
                    break
            items.append(self._render_list_item(content))
        tag = "ol" if ordered else "ul"
        attr = ' start="%d"' % start if ordered and start != 1 else ""
        body = "\n".join("<li>%s</li>" % item for item in items)
        out.append("<%s%s>\n%s\n</%s>" % (tag, attr, body, tag))
        return i

    def _render_list_item(self, lines):
        head = _inline(lines[0])
        rest = lines[1:]
        if not rest:
            return head
        strip = min(_indent_width(l) for l in rest)
        dedented = [l[strip:] if len(l) > strip else "" for l in rest]
        return head + "\n" + _Parser(dedented).parse()

    def _table(self, i, out):
        def cells(row):
            r = row.strip()
            if r.startswith("|"):
                r = r[1:]
            if r.endswith("|"):
                r = r[:-1]
            return [c.strip() for c in r.split("|")]

        header = cells(self.lines[i])
        aligns = []
        for cell in cells(self.lines[i + 1]):
            left, right = cell.startswith(":"), cell.endswith(":")
            aligns.append("center" if left and right
                          else "right" if right else "left" if left else None)
        rows = []
        i += 2
        while i < len(self.lines) and self.lines[i].strip() and "|" in self.lines[i]:
            rows.append(cells(self.lines[i]))
            i += 1

        def cell_html(text, align, tag):
            style = ' style="text-align:%s"' % align if align else ""
            return "<%s%s>%s</%s>" % (tag, style, _inline(text), tag)

        head = "".join(cell_html(c, a, "th") for c, a in zip(header, aligns))
        body = "\n".join(
            "<tr>%s</tr>" % "".join(cell_html(c, a, "td") for c, a in zip(row, aligns))
            for row in rows)
        out.append("<table>\n<thead>\n<tr>%s</tr>\n</thead>\n<tbody>\n%s\n</tbody>\n</table>"
                   % (head, body))
        return i

    def _paragraph(self, i, out):
        buf = [self.lines[i]]
        i += 1
        while i < len(self.lines) and self.lines[i].strip():
            line = self.lines[i]
            if (_FENCE_RE.match(line) or _HR_RE.match(line) or _HEADING_RE.match(line)
                    or _QUOTE_RE.match(line) or _LIST_RE.match(line)):
                break
            buf.append(line)
            i += 1
        out.append("<p>%s</p>" % _inline("\n".join(buf)))
        return i

    def _slug(self, text):
        slug = re.sub(r"[^\w\s-]", "", text.strip().lower())
        slug = re.sub(r"[\s_-]+", "-", slug).strip("-") or "section"
        if slug in self._slugs:
            self._slugs[slug] += 1
            slug = "%s-%d" % (slug, self._slugs[slug])
        else:
            self._slugs[slug] = 1
        return slug


def _inline(text, stash=None):
    """Render inline Markdown. ``stash`` holds finished HTML fragments that
    must survive the escaping pass (code spans, links, images)."""
    local = stash is None
    if local:
        stash = []

    def keep(html_fragment):
        stash.append(html_fragment)
        return "\x00%d\x00" % (len(stash) - 1)

    text = _CODESPAN_RE.sub(
        lambda m: keep("<code>%s</code>" % html.escape(m.group(2), quote=False)), text)
    text = _IMG_RE.sub(
        lambda m: keep('<img src="%s" alt="%s">'
                       % (html.escape(m.group(2), quote=True),
                          html.escape(m.group(1), quote=True))), text)

    def make_link(m):
        title = ' title="%s"' % html.escape(m.group(3), quote=True) if m.group(3) else ""
        return keep('<a href="%s"%s>%s</a>'
                    % (html.escape(m.group(2), quote=True), title,
                       _inline(m.group(1), stash)))

    text = _LINK_RE.sub(make_link, text)
    text = html.escape(text, quote=False)
    text = _DEL_RE.sub(r"<del>\1</del>", text)
    text = _BOLD_RE.sub(lambda m: "<strong>%s</strong>" % (m.group(1) or m.group(2)), text)
    text = _EM_RE.sub(lambda m: "<em>%s</em>" % (m.group(1) or m.group(2)), text)

    if local:
        text = re.sub(r"\x00(\d+)\x00", lambda m: stash[int(m.group(1))], text)
    return text
