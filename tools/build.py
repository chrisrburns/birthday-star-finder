#!/usr/bin/env python3
"""Build index.html by embedding a star catalog CSV into src/template.html.

Usage:
    python3 tools/build.py                       # uses data/Gaia_NS_bright_merge.csv
    python3 tools/build.py path/to/catalog.csv   # any CSV with the same columns
    python3 tools/build.py catalog.csv -o out.html

Only the Python standard library is needed.
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CSV = os.path.join(ROOT, "data", "Gaia_NS_bright_merge.csv")
TEMPLATE = os.path.join(ROOT, "src", "template.html")
REQUIRED = ("RA_ICRS", "DE_ICRS", "Plx")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", nargs="?", default=DEFAULT_CSV, help="catalog CSV to embed")
    ap.add_argument("-o", "--out", default=os.path.join(ROOT, "index.html"), help="output HTML file")
    args = ap.parse_args()

    with open(args.csv, encoding="utf-8-sig") as f:
        csv_text = f.read()
    header = [h.strip() for h in csv_text.splitlines()[0].split(",")]
    missing = [c for c in REQUIRED if c not in header]
    if missing:
        sys.exit(f"error: {args.csv} is missing required column(s): {', '.join(missing)}")

    with open(TEMPLATE, encoding="utf-8") as f:
        page = f.read()
    for marker in ("/*CSV*/", "/*CATNAME*/"):
        if marker not in page:
            sys.exit(f"error: template has no {marker} marker")

    # "</" inside a <script> block would end it early, so escape it
    page = page.replace("/*CSV*/", csv_text.replace("</", "<\\/"), 1)
    page = page.replace("/*CATNAME*/", os.path.basename(args.csv), 1)

    # The template has no <html>/<head>/<body> wrapper; add a minimal one so the file
    # is a complete document when opened directly or served by GitHub Pages.
    if not page.lstrip().lower().startswith("<!doctype"):
        page = ('<!doctype html>\n<html lang="en">\n<head>\n'
                + page.replace("</style>", "</style>\n</head>\n<body>", 1)
                + "\n</body>\n</html>\n")

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(page)
    rows = max(0, len([l for l in csv_text.splitlines() if l.strip()]) - 1)
    print(f"wrote {os.path.relpath(args.out)} ({len(page)/1024:.0f} KB, {rows} catalog rows)")


if __name__ == "__main__":
    main()
