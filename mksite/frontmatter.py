"""Tiny front-matter parser for ``key: value`` blocks delimited by ``---``.

Supported value types:

* strings (single/double quotes optional)
* integers and floats
* booleans (``true`` / ``false``)
* lists written as ``[a, b, c]``

Example::

    ---
    title: Hello World
    date: 2026-10-24
    tags: [python, ssg]
    draft: false
    ---

    Body text starts here.
"""

import re
from pathlib import Path

__all__ = ["parse", "parse_file"]

_LIST_RE = re.compile(r"^\[(.*)\]$")


def parse(text):
    """Split a document into ``(metadata dict, body text)``."""
    if not text.startswith("---"):
        return {}, text
    lines = text.split("\n")
    end = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end = idx
            break
    if end is None:
        return {}, text
    meta = {}
    for raw in lines[1:end]:
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        meta[key.strip()] = _convert(value.strip())
    return meta, "\n".join(lines[end + 1:])


def parse_file(path):
    """Read a file and return ``(metadata, body)``."""
    return parse(Path(path).read_text(encoding="utf-8-sig"))


def _convert(value):
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    lowered = value.lower()
    if lowered in ("true", "false"):
        return lowered == "true"
    m = _LIST_RE.match(value)
    if m:
        inner = m.group(1).strip()
        if not inner:
            return []
        return [_convert(item.strip()) for item in inner.split(",")]
    for caster in (int, float):
        try:
            return caster(value)
        except ValueError:
            pass
    return value
