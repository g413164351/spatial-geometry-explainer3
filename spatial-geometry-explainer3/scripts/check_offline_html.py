#!/usr/bin/env python3
"""Static offline HTML triage, NOT a substitute for browser testing.

Usage: python check_offline_html.py lesson.html
Outputs nonzero status for likely external dependencies; it is safe to run with stdlib.
"""
from __future__ import annotations
import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

class Scan(HTMLParser):
    def __init__(self):
        super().__init__()
        self.remote = []
        self.scripts = 0
        self.canvases = 0
        self.inputs = 0
        self.buttons = 0

    def handle_starttag(self, tag, attrs):
        kv = dict(attrs)
        if tag == "script": self.scripts += 1
        if tag == "canvas": self.canvases += 1
        if tag == "button": self.buttons += 1
        if tag == "input": self.inputs += 1
        if tag in {"script", "img", "iframe", "link", "video", "audio", "source", "object"}:
            for key in ("src", "href", "data"):
                url = kv.get(key, "") or ""
                if url.startswith(("http://", "https://", "//")):
                    self.remote.append(f"<{tag} {key}={url[:120]}>")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("html", type=Path)
    args = p.parse_args()
    if not args.html.is_file():
        p.error(f"File not found: {args.html}")
    source = args.html.read_text(encoding="utf-8")
    parser = Scan()
    parser.feed(source)
    # Detect popular runtime network APIs; may over-report benign comments/string literals.
    patterns = [r"\bfetch\s*\(\s*['\"]https?://", r"\bimport\s*\(\s*['\"]https?://",
                r"\bWebSocket\s*\(\s*['\"]wss?://", r"@import\s+(?:url\()?['\"]?https?://"]
    suspicious = [pattern for pattern in patterns if re.search(pattern, source, re.IGNORECASE)]
    print(f"File: {args.html.name} / {len(source)} chars")
    print(f"UI: {parser.canvases} canvas, {parser.scripts} scripts, {parser.buttons} buttons, {parser.inputs} inputs")
    if parser.remote or suspicious:
        for finding in parser.remote: print("EXTERNAL RESOURCE:", finding)
        for finding in suspicious: print("POSSIBLE NETWORK CALL:", finding)
        print("FAIL: not safe to claim self-contained offline HTML")
        return 1
    print("PASS: no obvious external resources found (static check only)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
