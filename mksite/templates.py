"""Minimal ``{{ placeholder }}`` template renderer.

Variables are looked up in a mapping; unknown keys render as empty strings,
so templates can reference optional metadata (``description``, ``tags`` …)
without extra wiring.
"""

import re

__all__ = ["render"]

_VAR_RE = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")


def render(template, mapping):
    """Replace ``{{ key }}`` occurrences with values from ``mapping``."""
    def substitute(match):
        return str(mapping.get(match.group(1), ""))
    return _VAR_RE.sub(substitute, template)
