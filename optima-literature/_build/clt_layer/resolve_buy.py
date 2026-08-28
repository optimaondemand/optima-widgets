# -*- coding: utf-8 -*-
"""Resolve a real purchase edition for each CLT title with no free text.

Open Library is the bibliographic authority here, as it is in
resolve_editions.py. Nothing is invented: an entry with no confident match is
written out with isbn=None and a needs_sourcing note, which shows on the card
as an open gap rather than a fabricated ISBN.
"""
import json, sys, io, time, urllib.parse, urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              errors="replace")

UA = "Optima-curriculum-build/1.0 (jdrexel@optimaed.com)"


def ol(title, author):
    q = urllib.parse.urlencode({
        "title": title, "author": author, "limit": 5,
        "fields": ("key,title,author_name,first_publish_year,isbn,publisher,"
                   "edition_count,cover_edition_key,language"),
    })
    req = urllib.request.Request("https://openlibrary.org/search.json?" + q,
                                 headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode("utf8"))


res = json.load(open("clt_resolved.json", encoding="utf-8"))
todo = [o for o in res if o["outcome"] == "purchase"]
print("resolving %d purchase editions\n" % len(todo))

out = {}
for i, o in enumerate(todo, 1):
    title, author = o["work"], o["author"]
    try:
        d = ol(title, author)
        docs = d.get("docs") or []
    except Exception as e:
        print("  %2d %-24s NETWORK FAIL %s" % (i, o["bank"][:24], e))
        out[o["bank"]] = {"isbn": None, "note": "openlibrary lookup failed"}
        continue
    pick = None
    for doc in docs:
        isbns = [s for s in (doc.get("isbn") or []) if len(s) == 13]
        if isbns:
            pick = (doc, sorted(isbns)[0])
            break
    if pick:
        doc, isbn = pick
        out[o["bank"]] = {
            "isbn": isbn,
            "ol_title": doc.get("title"),
            "ol_authors": doc.get("author_name"),
            "first_publish_year": doc.get("first_publish_year"),
            "publisher": (doc.get("publisher") or [None])[0],
            "url": "https://openlibrary.org" + doc["key"],
        }
        print("  %2d %-24s %-40s ISBN %s" % (i, o["bank"][:24],
                                             (doc.get("title") or "")[:40], isbn))
    else:
        out[o["bank"]] = {"isbn": None, "note": "no ISBN-13 in Open Library"}
        print("  %2d %-24s %-40s -- no ISBN found" % (i, o["bank"][:24],
                                                      title[:40]))
    time.sleep(1.0)

json.dump(out, open("clt_buy.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\nresolved with ISBN: %d / %d"
      % (sum(1 for v in out.values() if v.get("isbn")), len(todo)))
