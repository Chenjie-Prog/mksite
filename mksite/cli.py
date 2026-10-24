"""Command-line interface: ``init`` / ``build`` / ``serve`` / ``new``."""

import argparse
import datetime
import re
import sys
from pathlib import Path

from . import __version__, build as build_mod, scaffold, server
from .build import MksiteError

__all__ = ["main"]


def main(argv=None):
    parser = _make_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args) or 0
    except MksiteError as exc:
        print("[mksite] 错误：%s" % exc, file=sys.stderr)
        return 1


def _make_parser():
    parser = argparse.ArgumentParser(
        prog="mksite",
        description="零依赖的纯 Python 静态站点生成器（%s）" % __version__)
    parser.add_argument("--version", action="version",
                        version="mksite %s" % __version__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="初始化一个新站点")
    p_init.add_argument("dir", nargs="?", default=".", help="目标目录（默认当前目录）")
    p_init.set_defaults(func=_cmd_init)

    p_build = sub.add_parser("build", help="构建静态站点")
    p_build.add_argument("-s", "--source", default=".", help="站点源目录（默认当前目录）")
    p_build.add_argument("-o", "--output", default=None,
                         help="输出目录（默认 <source>/public）")
    p_build.set_defaults(func=_cmd_build)

    p_serve = sub.add_parser("serve", help="本地预览（自动监测改动并重建）")
    p_serve.add_argument("-s", "--source", default=".", help="站点源目录")
    p_serve.add_argument("-o", "--output", default=None, help="输出目录")
    p_serve.add_argument("-p", "--port", type=int, default=8000, help="端口（默认 8000）")
    p_serve.add_argument("--no-watch", action="store_true", help="关闭自动重建")
    p_serve.set_defaults(func=_cmd_serve)

    p_new = sub.add_parser("new", help="新建一篇文章")
    p_new.add_argument("title", help="文章标题")
    p_new.add_argument("-s", "--source", default=".", help="站点源目录")
    p_new.set_defaults(func=_cmd_new)
    return parser


def _cmd_init(args):
    root = Path(args.dir)
    files = {
        "site.json": scaffold.SITE_JSON,
        "templates/page.html": scaffold.PAGE_TEMPLATE,
        "static/style.css": scaffold.STYLE_CSS,
        "content/index.md": scaffold.INDEX_MD,
        "content/about.md": scaffold.ABOUT_MD,
        ".gitignore": scaffold.GITIGNORE,
    }
    for rel, text in files.items():
        dest = root / rel
        if dest.exists():
            print("[mksite] 跳过已存在文件 %s" % dest)
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        print("[mksite] 已创建 %s" % dest)
    print("[mksite] 初始化完成。运行 `mksite serve -s %s` 开始预览。" % args.dir)
    return 0


def _cmd_build(args):
    result = build_mod.build(args.source, args.output)
    print("[mksite] 构建完成：%d 个页面 → %s" % (result["pages"], result["output"]))
    return 0


def _cmd_serve(args):
    out = args.output or str(Path(args.source) / "public")
    server.serve(args.source, out, port=args.port, watch=not args.no_watch)
    return 0


def _cmd_new(args):
    root = Path(args.source)
    posts = root / "content" / "posts"
    posts.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()
    slug = _slugify(args.title)
    dest = posts / ("%s-%s.md" % (today, slug))
    n = 1
    while dest.exists():
        n += 1
        dest = posts / ("%s-%s-%d.md" % (today, slug, n))
    dest.write_text(
        scaffold.POST_MD.format(title=args.title, date=today), encoding="utf-8")
    print("[mksite] 已创建 %s" % dest)
    return 0


def _slugify(title):
    slug = re.sub(r"[\\/:*?\"<>|\s]+", "-", title.strip())
    slug = slug.strip("-.")
    return slug or "untitled"


if __name__ == "__main__":
    sys.exit(main())
