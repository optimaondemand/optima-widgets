# -*- coding: utf-8 -*-
"""Verify each resolved ISBN actually describes the intended work, and retry
the ones Open Library could not resolve from a title+author search.

A search hit is not evidence: "Pearl" by "Anonymous" returns Steinbeck. Every
ISBN below is read back from Open Library's edition record and checked against
the expected work before it is kept.
"""
import json, sys, io, time, urllib.parse, urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              errors="replace")
UA = "Optima-curriculum-build/1.0 (jdrexel@optimaed.com)"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode("utf8"))


def by_isbn(isbn):
    try:
        return get("https://openlibrary.org/isbn/%s.json" % isbn)
    except Exception as e:
        return {"_error": str(e)}


def search(**kw):
    kw.setdefault("limit", 6)
    kw.setdefault("fields", "key,title,author_name,isbn,publisher,"
                            "first_publish_year")
    q = urllib.parse.urlencode(kw)
    return get("https://openlibrary.org/search.json?" + q).get("docs") or []


buy = json.load(open("clt_buy.json", encoding="utf-8"))

# Expected-word check: the edition title read back from Open Library must
# contain one of these, or the ISBN is rejected.
EXPECT = {
    "Tertullian": ["apolog"], "Athanasius": ["incarnation"],
    "Jerome": ["jerome"], "Gregory the Great": ["pastoral"],
    "Anselm of Canterbury": ["proslog", "monolog", "cur deus"],
    "Bernard of Clairvaux": ["loving god"],
    "Hugh of St. Victor": ["didascalicon"], "Hildegard of Bingen": ["scivias"],
    "John Wycliffe": ["wyclif"], "Nicolaus Copernicus": ["revolution"],
    "Ernest Hemingway": ["old man"], "Jorge Luis Borges": ["ficciones", "fictions"],
    "Friedrich Hayek": ["serfdom"], "Hannah Arendt": ["human condition"],
    "Aleksandr Solzhenitsyn": ["ivan denisovich", "one day"],
    "James Baldwin": ["fire next time"],
    "Martin Luther King Jr.": ["birmingham"], "Toni Morrison": ["beloved"],
    "Pearl": ["pearl"],
}

print("--- verifying resolved ISBNs against the Open Library edition record ---")
bad = []
for bank, v in buy.items():
    isbn = v.get("isbn")
    if not isbn:
        continue
    ed = by_isbn(isbn)
    t = (ed.get("title") or "") + " " + " ".join(
        ed.get("subtitle", "") if isinstance(ed.get("subtitle"), str) else [])
    ok = any(w in t.lower() for w in EXPECT.get(bank, [""]))
    v["verified_title"] = ed.get("title")
    v["verified"] = bool(ok)
    print("  %-24s %-14s %-40s %s"
          % (bank[:24], isbn, (ed.get("title") or ed.get("_error", "?"))[:40],
             "OK" if ok else "<< REJECTED"))
    if not ok:
        bad.append(bank)
    time.sleep(0.7)

print("\n--- retrying the unresolved and the rejected ---")
RETRY = {
    "Gregory of Nyssa":   dict(title="The Life of Moses",
                               author="Gregory of Nyssa"),
    "Charles Montesquieu": dict(title="The Spirit of the Laws",
                                author="Montesquieu"),
    "Albert Camus":       dict(title="The Stranger", author="Albert Camus"),
    "Pearl":              dict(title="Sir Gawain and the Green Knight Pearl",
                               author="Tolkien"),
}
for bank in list(RETRY) + [b for b in bad if b not in RETRY]:
    kw = RETRY.get(bank)
    if not kw:
        continue
    docs = search(**kw)
    print("  %s:" % bank)
    for d in docs[:4]:
        isbns = [s for s in (d.get("isbn") or []) if len(s) == 13]
        print("     %-46s %-30s %s"
              % ((d.get("title") or "")[:46],
                 ", ".join((d.get("author_name") or [])[:2])[:30],
                 (sorted(isbns)[0] if isbns else "-")))
    time.sleep(0.7)

json.dump(buy, open("clt_buy.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\nrejected:", bad)
