#!/usr/bin/env python3
"""Deterministic manifest sanity check for penpot-ux-guardian.

Usage: python3 check-manifest.py <penpot.design-system.md>

Checks: duplicate token/component names, components missing a canonical
Penpot ref, token refs used in component sections that are never defined.
Exits non-zero on failure. Markdown-aware but intentionally shallow: the
agent's live Penpot inspection remains authoritative.
"""

import re
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <manifest.md>", file=sys.stderr)
        return 2
    text = Path(sys.argv[1]).read_text()

    errors: list[str] = []

    tables: list[str] = []
    for m in re.finditer(r"(?m)^\s*\|([^|]*)\|", text):
        cell = m.group(1)
        bt = re.search(r"`([^`]+)`", cell)
        if bt:
            tables.append(bt.group(1))
    seen: set[str] = set()
    for tok in tables:
        name = tok.strip("`")
        if name in seen:
            errors.append(f"duplicate token/component name: {name}")
        seen.add(name)

    warnings: list[str] = []
    for m in re.finditer(r"^###\s+(`[^`]+`)", text, re.M):
        comp = m.group(1)
        section = text[m.start() : m.start() + 1200]
        if "canonical ref" not in section.lower():
            errors.append(f"{comp}: missing canonical Penpot ref line")
        elif "<penpot" in section:
            warnings.append(f"{comp}: canonical Penpot ref is still a placeholder")

    defined = {t.strip("`") for t in tables}
    used = set(re.findall(r"`((?:color|spacing|type|radius|border|effect)[^`]*)`", text))
    undefined = sorted(u for u in used if u not in defined)
    if undefined:
        errors.append(f"undefined token refs used: {', '.join(undefined)}")

    if errors:
        print("FAIL manifest check:")
        for e in errors:
            print(f"  - {e}")
        return 1
    for w in warnings:
        print(f"warning: {w}")
    print("PASS manifest check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
