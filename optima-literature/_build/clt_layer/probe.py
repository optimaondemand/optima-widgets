# -*- coding: utf-8 -*-
"""Dump the real Gutenberg holdings for a given author token, so a selection is
made from what exists rather than from what a title is assumed to be called."""
import csv, sys, re, unicodedata, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def strip(s):
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c))

ALL = list(csv.DictReader(open("pg_catalog.csv", encoding="utf-8")))
EN = [r for r in ALL if r["Type"] == "Text" and r["Language"] == "en"]

for tok in sys.argv[1:]:
    tok = tok.lower()
    pool = [r for r in EN if tok in strip(r["Authors"] or "").lower()]
    anylang = [r for r in ALL if tok in strip(r["Authors"] or "").lower()]
    intitle = [r for r in EN if tok in strip(r["Title"] or "").lower()]
    print("=" * 78)
    print("%s  (en-by-author %d | any-lang-by-author %d | en-in-title %d)"
          % (tok, len(pool), len(anylang), len(intitle)))
    for r in pool[:14]:
        print("   A %-6s %-64s | %s"
              % (r["Text#"], r["Title"].replace("\n", " ")[:64],
                 r["Authors"][:34]))
    if not pool:
        for r in anylang[:6]:
            print("   L %-6s [%s] %-58s | %s"
                  % (r["Text#"], r["Language"],
                     r["Title"].replace("\n", " ")[:58], r["Authors"][:30]))
        for r in intitle[:8]:
            print("   T %-6s %-64s | %s"
                  % (r["Text#"], r["Title"].replace("\n", " ")[:64],
                     r["Authors"][:34]))
