"""
smoke_resolve.py — prove the resolver works on a handful of records before
turning it loose on 226. Deliberately picks the awkward cases, not the easy ones:
a Penguin classic (translator likely), a Folger edition (editor likely), and a
Kindle ASIN that cannot be looked up by ISBN at all.
"""
import json
from pathlib import Path

import resolve_editions as R

DATA = Path(__file__).resolve().parent.parent / "data"

WANT = [
    "Emma",                       # plain ISBN, no translator expected
    "Romeo and Juliet",           # Folger -> editor expected
    "The Canterbury Tales",       # Penguin -> Coghill translator expected
    "Electra",                    # Kindle ASIN -> must fall back to title
    "The Divine Comedy",          # Ciardi translator expected
    "The Odyssey",                # a.co shortener -> must resolve first
]


def main():
    book = json.loads((DATA / "stage1_records.json").read_text(encoding="utf8"))["booklist"]
    cache = R.load_cache()
    picked = []
    for want in WANT:
        for b in book:
            if b["title"].strip().lower() == want.lower():
                picked.append(b)
                break

    print(f"testing {len(picked)} of {len(WANT)} requested records\n")
    for b in picked:
        asin, url = b.get("asin"), b.get("url")
        route = "isbn"
        if not asin and b.get("url_kind") == "amazon_short" and url:
            final = R.resolve_short(url, cache)
            asin = R.asin_of(final)
            route = f"a.co -> {asin or 'FAILED'}"

        if R.is_isbn10(asin):
            res = R.ol_by_isbn(asin, cache)
        else:
            res = R.ol_by_title(b["title"], b.get("author"), cache)
            route += " -> title-search"

        print(f"G{b['grade']:>2}  {b['title']}")
        print(f"     route        : {route}")
        print(f"     ok           : {res.get('ok')}  {res.get('error','')}")
        print(f"     edition title: {res.get('edition_title') or res.get('work_title')}")
        print(f"     publisher    : {res.get('publishers')}")
        print(f"     edition date : {res.get('publish_date')}")
        print(f"     OL first pub : {res.get('ol_first_publish_raw')}  (UNTRUSTED)")
        print(f"     by_statement : {str(res.get('by_statement'))[:90]}")
        print(f"     contributions: {str(res.get('contributions'))[:90]}")
        print(f"     ROLES        : {res.get('roles')}")
        print()
    R.save_cache(cache)


if __name__ == "__main__":
    main()
