# -*- coding: utf-8 -*-
"""Match each editorial selection to a real Project Gutenberg English text.

Gutenberg only distributes US-public-domain works, so a confident match IS the
copyright clearance -- the same safety rule match_free.py already runs on.
No match means "resolve a purchase edition instead", never "assume it is free".
"""
import csv, re, json, unicodedata, difflib
import selection as sel

STOP = {"the", "a", "an", "of", "on", "and", "in", "to", "de"}


def strip(s):
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c))


def toks(s):
    return [t for t in re.findall(r"[a-z0-9]+", strip(s).lower()) if t not in STOP]


rows = [r for r in csv.DictReader(open("pg_catalog.csv", encoding="utf-8"))
        if r["Type"] == "Text" and r["Language"] == "en"]

hits, misses = {}, []
for bank, work, author, atok in sel.SEL:
    wt = toks(work)
    if atok:
        pool = [r for r in rows if atok in strip(r["Authors"] or "").lower()]
    else:
        # anonymous work: match on title across the whole catalogue
        pool = rows
    best, bestsc = None, 0.0
    for r in pool:
        rt = toks(r["Title"])
        if not rt:
            continue
        overlap = len(set(wt) & set(rt)) / max(1, len(set(wt)))
        ratio = difflib.SequenceMatcher(
            None, " ".join(wt), " ".join(rt)).ratio()
        sc = 0.7 * overlap + 0.3 * ratio
        # prefer complete/standalone editions over single volumes of a set
        if re.search(r"volume\s+([2-9]|1\d)", r["Title"].lower()):
            sc -= 0.08
        if sc > bestsc:
            best, bestsc = r, sc
    if best and bestsc >= 0.62:
        hits[bank] = {
            "bank": bank, "work": work, "author": author,
            "gid": int(best["Text#"]), "pg_title": best["Title"],
            "pg_authors": best["Authors"], "issued": best["Issued"],
            "subjects": best["Subjects"], "locc": best["LoCC"],
            "score": round(bestsc, 3),
        }
    else:
        misses.append({"bank": bank, "work": work, "author": author,
                       "pool": len(pool), "score": round(bestsc, 3),
                       "best": best["Title"] if best else None})

json.dump(hits, open("pg_hits.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(misses, open("pg_misses.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("matched on Gutenberg: %d / %d" % (len(hits), len(sel.SEL)))
print("no confident match  : %d" % len(misses))
print()
print("--- LOW-CONFIDENCE MATCHES (review these) ---")
for h in sorted(hits.values(), key=lambda x: x["score"])[:18]:
    print("  %.2f  %-26s %-42s -> PG %-6d %s"
          % (h["score"], h["bank"][:26], h["work"][:42], h["gid"],
             h["pg_title"][:60]))
print()
print("--- NO MATCH (need a purchase edition) ---")
for m in misses:
    print("  %-28s %-46s (pool %4d, best %.2f: %s)"
          % (m["bank"][:28], m["work"][:46], m["pool"], m["score"],
             (m["best"] or "-")[:44]))
