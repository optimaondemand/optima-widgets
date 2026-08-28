# -*- coding: utf-8 -*-
"""Emit _build/clt_additions.py -- the CLT layer as stage3-shaped records."""
import json, io, sys, re, unicodedata, datetime
import dates as D
import selection as sel
import shelves as S

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              errors="replace")

OUT = ('C:/Users/JessicaDrexel/Documents/GitHub/optima-widgets'
       '/optima-literature/_build/clt_additions.py')
res = json.load(open("clt_resolved.json", encoding="utf-8"))
buy = json.load(open("clt_buy.json", encoding="utf-8"))

# Corrections made after reading the Open Library edition record back. The
# search hit was wrong or missing in each case; each replacement was verified
# by ISBN lookup (fix_buy.py).
BUY_FIX = {
    "Pearl": ("9780007375929",
              "Sir Gawain and the Green Knight: With Pearl and Sir Orfeo",
              "HarperCollins",
              "search returned Steinbeck's The Pearl; this is the Tolkien "
              "translation of the Middle English poem"),
    "Charles Montesquieu": ("9780521369749", "The Spirit of the Laws",
                            "Cambridge University Press", None),
    "Albert Camus": ("9780679720201", "The Stranger", "Vintage International",
                     None),
    "Gregory of Nyssa": ("9780809121120",
                         "Gregory of Nyssa: The Life of Moses", "Paulist Press",
                         None),
    "Hildegard of Bingen": ("9780809104314", "Hildegard of Bingen: Scivias",
                            "Paulist Press", None),
}


def norm_key(title, author):
    """Same shape parse_sources.joinkey builds: normalised title|surname."""
    def n(s):
        s = unicodedata.normalize("NFKD", s or "")
        s = "".join(c for c in s if not unicodedata.combining(c))
        return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()
    a = n(author).split()
    return "%s|%s" % (n(title), a[-1] if a else "")


records, existing, omitted = [], [], []
OMIT = getattr(sel, "OMIT", {})
for o in res:
    bank = o["bank"]
    if bank in OMIT:
        omitted.append({"bank": bank, "reason": OMIT[bank]})
        continue
    if o["outcome"] == "existing":
        existing.append(o)
        continue

    year, circa = D.YEARS.get(bank, (None, False))
    en = bank in D.ENGLISH_ORIGINAL

    if o["outcome"] == "gutenberg":
        title = o["pg_title"]
        # Gutenberg distributes only US-public-domain works, so the match is
        # the clearance. English-original means the free text IS the text;
        # anything else reaches the reader through one particular translation.
        free = {
            "state": "identical" if en else "similar",
            "reason": None,
            "free": {
                "url": o["url"],
                "source": "gutenberg.org",
                "gutenberg_id": o["gid"],
                "matched_title": o["pg_title"],
                "via": "clt-additions",
            },
            "read_online": None,
            "note": None if en else
                    "Public-domain translation. A modern translation will "
                    "differ in wording.",
        }
        # No purchase edition is resolved for a public-domain text, so the
        # card carries the free link only. Setting url here would render a
        # "buy" button pointing at Gutenberg beside the free one.
        edition, url, isbn = {}, None, None
    else:
        b = dict(buy.get(bank) or {})
        if bank in BUY_FIX:
            i, t, p, why = BUY_FIX[bank]
            b = {"isbn": i, "ol_title": t, "publisher": p, "fix_note": why}
        title = o["work"]
        isbn = b.get("isbn")
        free = {
            "state": "none",
            "reason": ("in_copyright" if "copyright" in (o.get("why") or "")
                       else "needs_sourcing"),
            "free": None,
            "read_online": None,
            "note": o.get("why"),
        }
        edition = {
            "ok": bool(isbn),
            "isbn": isbn,
            "edition_title": b.get("ol_title"),
            "publishers": [b.get("publisher")] if b.get("publisher") else [],
            "publish_date": None,
            "roles": {},
        }
        url = ("https://openlibrary.org/isbn/%s" % isbn) if isbn else None

    records.append({
        "grade": "CLT",
        "listed_as": None,
        "title": title,
        "author": o["author"],
        "authors": None,
        "kind": None,
        "edition_hint": None,
        "notes": [],
        "url": url,
        "url_kind": "gutenberg" if o["outcome"] == "gutenberg" else "openlibrary",
        "asin": None,
        "extra_urls": [],
        "listed_count": 0,
        "key": norm_key(title, o["author"]),
        "review": None,
        "edition": edition,
        "free_version": free,
        # --- CLT layer's own fields
        "clt_bank_entry": bank,
        "clt_shelf": S.SHELF[bank],
        "clt_only": True,
        "clt_year": year,
        "clt_circa": circa,
        "clt_english_original": en,
        "clt_selection_note": o.get("why"),
    })

# key collisions would silently merge two cards in any key-driven lookup
seen = {}
for r in records:
    seen.setdefault(r["key"], []).append(r["title"])
dupes = {k: v for k, v in seen.items() if len(v) > 1}

hdr = '''# -*- coding: utf-8 -*-
"""clt_additions.py -- the CLT Author Bank layer of the catalogue.

WHY THIS FILE EXISTS
--------------------
The catalogue is generated from the OAO book list, so every one of its 226
original records is on that list by construction. The CLT badge added on
2026-08-27 could therefore only mark titles that were ALREADY there: 42 cards,
covering 30 of the bank's 162 entries. The remaining 132 entries -- Augustine,
Aquinas, Cicero, Plutarch, Milton, Locke, Tolstoy and most of the rest -- had
no title in the library at all.

These records close that gap. They are NOT on the OAO book list, no Optima
course assigns them, and nothing here should ever be read as required
purchasing. `grade` is the sentinel "CLT" for exactly that reason.

WHAT CLT ACTUALLY PUBLISHES
---------------------------
An AUTHOR list, at https://www.cltexam.com/tests/authors/ -- never a list of
works. So the choice of which work represents each author is Optima's
editorial judgement, not CLT's, and is open to revision. What is NOT judgement
is the bibliography: every Gutenberg id below was read out of Gutenberg's own
catalogue export, and every ISBN was read back from the Open Library edition
record before it was written here.

RIGHTS
------
Gutenberg distributes only US-public-domain works, so a confident Gutenberg
match IS the clearance -- the same rule match_free.py runs on. The %d entries
with no public-domain English text carry a purchase edition instead and are
marked state "none"; they are never linked to a convenient free PDF.

TRAPS FOUND WHILE BUILDING THIS, worth not rediscovering:
  * Author-name matching produces confident nonsense. "Jerome" matches Jerome
    K. Jerome, "Bernard" matches Bernard Shaw, "Hildegard" matches Hildegard
    Frey's Camp Fire Girls, "Anselm" matched a Confederate war history. Every
    match here was confirmed against the catalogue row by eye.
  * A title search is not a verification either. Searching Open Library for
    "Pearl" by "Anonymous" returns Steinbeck's The Pearl, and it passes any
    keyword check that looks for the word "pearl".
  * Gutenberg's language column is multi-valued. Wittgenstein's Tractatus is
    "de; en" and an en-only filter drops it.
  * Three bank entries were already in the catalogue under records with an
    EMPTY author field, so author matching could not see them: Confucian
    Analects, the Nietzsche excerpts, and the Federalist Papers. Those are
    badged in clt_titles.py, NOT duplicated here.

Generated %s by _build/clt_layer/gen_additions.py; see that folder's README.
"""

# Records in stage3 shape, merged into the book list at build time.
ADDITIONS = %s

# Bank entries satisfied by a record the catalogue already holds.
ALREADY_IN_CATALOGUE = %s

# Bank entries deliberately given no title. The gate counts an omission here as
# accounted for, so a bank entry can never disappear by accident -- only on the
# record, with a reason.
OMITTED = %s
'''

body = json.dumps(records, ensure_ascii=False, indent=1)
body = body.replace(": true", ": True").replace(": false", ": False") \
           .replace(": null", ": None")
exist = json.dumps([{"bank": e["bank"], "grade": e["grade"],
                     "title": e["title"]} for e in existing],
                   ensure_ascii=False, indent=1)
exist = exist.replace(": null", ": None")

open(OUT, "w", encoding="utf-8").write(
    hdr % (sum(1 for r in records if r["free_version"]["state"] == "none"),
           datetime.date.today().isoformat(), body, exist,
           json.dumps(omitted, ensure_ascii=False, indent=1)))

print("records: %d  (free %d / purchase %d)"
      % (len(records),
         sum(1 for r in records if r["free_version"]["state"] != "none"),
         sum(1 for r in records if r["free_version"]["state"] == "none")))
print("already in catalogue:", [e["bank"] for e in existing])
print("omitted:", [o["bank"] for o in omitted] or "none")
print("duplicate keys:", dupes or "none")
print("records with no year:",
      [r["title"] for r in records if r["clt_year"] is None] or "none")
print("purchase records with no ISBN:",
      [r["title"] for r in records
       if r["free_version"]["state"] == "none" and not r["edition"].get("isbn")]
      or "none")
