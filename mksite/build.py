"""Build pipeline: read a site source tree, render pages, copy assets and
generate index / RSS feed / sitemap."""

import email.utils
import html
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

from . import __version__, frontmatter, markdown, scaffold, templates

__all__ = ["build", "load_config"]

DEFAULT_CONFIG = {
    "name": "My Site",
    "language": "zh-CN",
    "base_url": "",
    "author": "",
}


class MksiteError(Exception):
    """Raised for user-facing build errors (bad config, missing dirs)."""


def load_config(src):
    path = Path(src) / "site.json"
    config = dict(DEFAULT_CONFIG)
    if path.exists():
        try:
            config.update(json.loads(path.read_text(encoding="utf-8-sig")))
        except json.JSONDecodeError as exc:
            raise MksiteError("site.json 解析失败: %s" % exc) from exc
    return config


def build(src=".", out=None, config=None):
    """Build the site at ``src`` into ``out`` (default ``src/public``).

    Returns a dict with the page count and output path.
    """
    src = Path(src)
    content_dir = src / "content"
    if not content_dir.is_dir():
        raise MksiteError("找不到 %s —— 请在站点目录中运行，或用 -s 指定源目录" % content_dir)

    config = dict(config) if config else load_config(src)
    out = Path(out) if out else src / "public"
    out.mkdir(parents=True, exist_ok=True)

    page_template = _load_template(src)
    _copy_static(src, out)

    pages = []
    for path in sorted(content_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(content_dir)
        if path.suffix.lower() == ".md":
            pages.append(_render_page(src, out, content_dir, rel, page_template, config))
        else:
            dest = out / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, dest)

    if not (content_dir / "index.md").exists():
        _render_index(out, page_template, config, pages)
        pages.append({"title": config["name"], "url": "index.html",
                      "date": "", "summary": config["name"]})

    dated = [p for p in pages if p.get("date")]
    dated.sort(key=lambda p: str(p["date"]), reverse=True)
    if config.get("base_url"):
        _write_feed(out, config, dated)
        _write_sitemap(out, config, pages)

    return {"pages": len(pages), "output": str(out)}


def _load_template(src):
    path = Path(src) / "templates" / "page.html"
    if path.exists():
        return path.read_text(encoding="utf-8-sig")
    return scaffold.PAGE_TEMPLATE


def _copy_static(src, out):
    static_dir = Path(src) / "static"
    if not static_dir.is_dir():
        return
    for path in static_dir.rglob("*"):
        if path.is_file():
            dest = out / path.relative_to(static_dir)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, dest)


def _render_page(src, out, content_dir, rel_md, page_template, config):
    meta, body = frontmatter.parse_file(content_dir / rel_md)
    content_html = markdown.md_to_html(body)
    rel_html = rel_md.with_suffix(".html")
    title = str(meta.get("title") or _first_heading(body) or rel_md.stem)
    root = _root_prefix(rel_html.parent)

    dest = out / rel_html
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(templates.render(page_template, {
        **config,
        **{k: v for k, v in meta.items() if not isinstance(v, (list, dict))},
        "title": title,
        "description": _meta_description(meta.get("description"), content_html),
        "content": content_html,
        "root": root,
        "generator": "mksite %s" % __version__,
    }), encoding="utf-8")

    return {
        "title": title,
        "url": rel_html.as_posix(),
        "date": str(meta.get("date", "")),
        "summary": _meta_description(meta.get("description"), content_html),
    }


def _render_index(out, page_template, config, pages):
    items = sorted((p for p in pages if p.get("date")),
                   key=lambda p: str(p["date"]), reverse=True)
    if items:
        listing = "\n".join(
            '<li><a href="%s">%s</a> <time>%s</time></li>'
            % (html.escape(p["url"], quote=True), html.escape(str(p["title"])),
               html.escape(str(p["date"])))
            for p in items)
        content = '<ul class="post-list">\n%s\n</ul>' % listing
    else:
        content = ""
    (out / "index.html").write_text(templates.render(page_template, {
        **config,
        "title": config["name"],
        "description": "",
        "content": content,
        "root": ".",
        "generator": "mksite %s" % __version__,
    }), encoding="utf-8")


def _write_feed(out, config, pages, limit=20):
    base = str(config["base_url"]).rstrip("/")
    items = []
    for page in pages[:limit]:
        link = "%s/%s" % (base, page["url"])
        pub_date = _rfc822_date(page["date"])
        items.append(
            "<item>\n"
            "    <title>%s</title>\n"
            "    <link>%s</link>\n"
            "    <guid>%s</guid>\n"
            "    %s\n"
            "    <description>%s</description>\n"
            "</item>"
            % (xml_escape(str(page["title"])), xml_escape(link), xml_escape(link),
               pub_date, xml_escape(str(page["summary"]))))
    feed = ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            "<rss version=\"2.0\">\n"
            "<channel>\n"
            "  <title>%s</title>\n"
            "  <link>%s</link>\n"
            "  <description>%s</description>\n"
            "  <generator>mksite %s</generator>\n"
            "%s\n"
            "</channel>\n"
            "</rss>\n"
            % (xml_escape(str(config["name"])), xml_escape(base),
               xml_escape(str(config.get("description", config["name"]))),
               __version__, "\n".join(items)))
    (out / "feed.xml").write_text(feed, encoding="utf-8")


def _write_sitemap(out, config, pages):
    base = str(config["base_url"]).rstrip("/")
    today = datetime.now(timezone.utc).date().isoformat()
    urls = "".join(
        "  <url>\n    <loc>%s</loc>\n    %s\n  </url>\n"
        % (xml_escape("%s/%s" % (base, p["url"])),
           "<lastmod>%s</lastmod>" % p["date"] if p.get("date")
           else "<lastmod>%s</lastmod>" % today)
        for p in pages)
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               "%s</urlset>\n" % urls)
    (out / "sitemap.xml").write_text(sitemap, encoding="utf-8")


def _first_heading(body):
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def _meta_description(explicit, content_html):
    if explicit:
        return str(explicit)
    text = re.sub(r"<[^>]+>", " ", content_html)
    text = re.sub(r"\s+", " ", html.unescape(text)).strip()
    return html.escape(text[:160], quote=True)


def _root_prefix(page_dir):
    parts = 0 if str(page_dir) == "." else len(Path(page_dir).parts)
    return "/".join([".."] * parts) if parts else "."


def _rfc822_date(value):
    try:
        dt = datetime.strptime(str(value)[:10], "%Y-%m-%d")
    except ValueError:
        return ""
    return "<pubDate>%s</pubDate>" % email.utils.format_datetime(
        dt.replace(tzinfo=timezone.utc))
