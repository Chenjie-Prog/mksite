"""Development server: serve the built site and rebuild on file changes."""

import http.server
import threading
import time
from functools import partial
from pathlib import Path

from .build import build

__all__ = ["serve", "watch_forever"]

_POLL_SECONDS = 0.7
_WATCHED_SUFFIXES = {".md", ".html", ".css", ".js", ".json", ".txt", ".xml", ".png",
                     ".jpg", ".jpeg", ".gif", ".svg", ".webp"}


class _Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Dev server: never let the browser cache stale pages.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        print("[mksite]", fmt % args)


def serve(src, out, port=8000, watch=True):
    """Build once, then serve ``out`` at http://127.0.0.1:<port>/ forever."""
    build(src, out)
    httpd = http.server.ThreadingHTTPServer(
        ("127.0.0.1", port), partial(_Handler, directory=str(Path(out))))
    if watch:
        threading.Thread(target=watch_forever, args=(src, out), daemon=True).start()
    print("[mksite] 预览地址 http://127.0.0.1:%d/ （按 Ctrl+C 停止）" % port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[mksite] 已停止")
    finally:
        httpd.server_close()


def watch_forever(src, out):
    """Poll the source tree and rebuild whenever a file changes."""
    snapshot = _scan(src)
    while True:
        time.sleep(_POLL_SECONDS)
        current = _scan(src)
        if current != snapshot:
            snapshot = current
            try:
                result = build(src, out)
                print("[mksite] 已重新构建：%d 个页面" % result["pages"])
            except Exception as exc:  # keep serving even if a rebuild fails
                print("[mksite] 重建失败：%s" % exc)


def _scan(src):
    state = {}
    root = Path(src)
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if rel.parts and rel.parts[0] == "public":
            continue  # never watch our own build output
        if path.suffix.lower() in _WATCHED_SUFFIXES:
            try:
                state[str(path)] = path.stat().st_mtime
            except OSError:
                pass
    return state
