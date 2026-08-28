# -*- coding: utf-8 -*-
"""Targeted title search across the Gutenberg catalogue.

Usage: python find.py "title words" ["author substring"]
Prints every English (or multi-language including English) text whose title
contains all the given words, with its author, so identity can be confirmed by
eye before a gid is written into the build.
"""
import csv, sys, io, re, unicodedata
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              errors="replace")


def strip(s):
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


ALL = list(csv.DictReader(open("pg_catalog.csv", encoding="utf-8")))
EN = [r for r in ALL
      if r["Type"] == "Text" and "en" in r["Language"].split("; ")]

words = strip(sys.argv[1]).split()
auth = strip(sys.argv[2]) if len(sys.argv) > 2 else None

for r in EN:
    t = strip(r["Title"])
    if all(w in t for w in words):
        if auth and auth not in strip(r["Authors"]):
            continue
        print("%-6s [%-6s] %-58s | %s"
              % (r["Text#"], r["Language"],
                 r["Title"].replace("\n", " ")[:58], r["Authors"][:44]))
