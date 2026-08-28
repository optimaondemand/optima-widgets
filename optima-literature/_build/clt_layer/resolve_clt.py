# -*- coding: utf-8 -*-
"""Turn the editorial selection into a resolution table.

Three outcomes per bank entry:
  gutenberg  a verified Project Gutenberg gid. Gutenberg only distributes
             US-public-domain works, so the match IS the clearance.
  purchase   no public-domain English text exists; a buy edition is resolved
             from Open Library instead.
  existing   the catalogue ALREADY holds a work by this author under a record
             whose author field is empty, so CLT author-matching could not see
             it. Badge that record; do not add a second card.
"""
import csv, json, sys, io, unicodedata
import selection as sel

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              errors="replace")

# Bank entries already in the catalogue under an author-less record. Keys are
# (grade, title) as build_reference_library sees them -- AFTER
# source_corrections runs, which is why the Federalist typo is not here.
EXISTING = {
    "Confucius":            ("12", "Confucian Analects"),
    "Friedrich Nietzsche":  ("12", "Excerpts from Nietzsche's writings"),
    "James Madison":        ("11", "The Federalist Papers"),
}

# Hand-resolved gids: the auto-matcher either missed these or matched the
# wrong work. Every one was confirmed by reading the catalogue row.
MANUAL = {
    "Hesiod":                 348,    # Works and Days, in the Evelyn-White volume
    "Hippocrates":            72583,
    "Herodotus":              2707,
    "Cicero":                 2808,    # De Amicitia + De Senectute
    "Julius Caesar":          10657,
    "Seneca the Younger":     56075,
    "Origen":                 70561,
    "Bede the Venerable":     38326,
    "Avicenna":               58186,
    "Peter Abelard":          14268,   # Historia Calamitatum
    "Averroes":               65708,
    "Catherine of Siena":     7403,
    "Christine de Pizan":     36737,
    "Martin Luther":          274,     # the Ninety-Five Theses, under its full title
    "Teresa of Avila":        8120,
    "Galileo Galilei":        46036,   # Sidereus Nuncius
    "Gottfried Leibniz":      17147,   # Theodicy
    "Jonathan Edwards":       34632,   # includes Sinners in the Hands of an Angry God
    "Soren Kierkegaard":      60333,
    "Susan B. Anthony":       28020,
    "Gregor Mendel":          69362,
    "Louis Pasteur":          63355,
    "Anton Chekhov":          1756,    # Uncle Vanya; PG has no Cherry Orchard
    "Mahatma Gandhi":         10366,   # Freedom's Battle
    "Ludwig Wittgenstein":    5740,    # bilingual record, missed by an en-only filter
    # --- auto-matcher picked a real author but the WRONG work:
    "Charles Darwin":         1228,    # was: the 1842/44 foundational essays
    "John Bunyan":            131,     # was: a one-syllable adaptation by Lucy Aikin
    "Mary Wollstonecraft":    3420,    # was: the Posthumous Works
}

# No public-domain English text on Gutenberg. Resolve a purchase edition.
PURCHASE = {
    "Tertullian":           "not on Gutenberg in any language",
    "Athanasius":           "Gutenberg holds only Latin and Greek",
    "Gregory of Nyssa":     "not on Gutenberg",
    "Jerome":               "not on Gutenberg; the surname collides with Jerome K. Jerome",
    "Gregory the Great":    "not on Gutenberg",
    "Anselm of Canterbury": "not on Gutenberg",
    "Bernard of Clairvaux": "not on Gutenberg; the forename collides with Bernard Shaw",
    "Hugh of St. Victor":   "not on Gutenberg",
    "Hildegard of Bingen":  "not on Gutenberg; the forename collides with Hildegard Frey",
    "John Wycliffe":        "not on Gutenberg; the surname collides with James Wycliffe Headlam",
    "Nicolaus Copernicus":  "not on Gutenberg in English",
    "Charles Montesquieu":  "Gutenberg holds only French and Finnish",
    "Pearl":                "the Middle English poem is not on Gutenberg; modern verse translations are in copyright",
    "Ernest Hemingway":     "in copyright",
    "Jorge Luis Borges":    "in copyright",
    "Friedrich Hayek":      "in copyright",
    "Hannah Arendt":        "in copyright",
    "Albert Camus":         "in copyright",
    "Aleksandr Solzhenitsyn": "in copyright",
    "James Baldwin":        "in copyright",
    "Martin Luther King Jr.": "in copyright",
    "Toni Morrison":        "in copyright",
}

ROWS = {r["Text#"]: r for r in csv.DictReader(
    open("pg_catalog.csv", encoding="utf-8"))}
hits = json.load(open("pg_hits.json", encoding="utf-8"))

out = []
for bank, work, author, tok in sel.SEL:
    if bank in EXISTING:
        g, t = EXISTING[bank]
        out.append({"bank": bank, "outcome": "existing", "author": author,
                    "grade": g, "title": t})
        continue
    if bank in PURCHASE:
        out.append({"bank": bank, "outcome": "purchase", "author": author,
                    "work": work, "why": PURCHASE[bank]})
        continue
    gid = MANUAL.get(bank) or (hits[bank]["gid"] if bank in hits else None)
    if gid is None:
        out.append({"bank": bank, "outcome": "UNRESOLVED", "author": author,
                    "work": work})
        continue
    r = ROWS[str(gid)]
    out.append({
        "bank": bank, "outcome": "gutenberg", "author": author,
        "work": work,
        "gid": gid,
        # The title we PRINT is Gutenberg's, so the card never promises a text
        # under a name the linked file does not carry.
        "pg_title": " ".join(r["Title"].split()),
        "pg_authors": r["Authors"],
        "language": r["Language"],
        "subjects": r["Subjects"],
        "locc": r["LoCC"],
        "url": "https://www.gutenberg.org/ebooks/%d" % gid,
    })

json.dump(out, open("clt_resolved.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

from collections import Counter
c = Counter(o["outcome"] for o in out)
print("resolution outcomes:", dict(c), " total", len(out))
bad = [o for o in out if o["outcome"] == "UNRESOLVED"]
print("unresolved:", [o["bank"] for o in bad])
# identity guard: the PG author string must mention the selection's author
print()
print("--- identity guard: PG author string vs expected surname ---")
def strip(s):
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
flag = 0
for o in out:
    if o["outcome"] != "gutenberg":
        continue
    surs = [w for w in strip(o["author"]).replace(".", " ").split() if len(w) > 3]
    if not any(s in strip(o["pg_authors"]) or s in strip(o["pg_title"])
               for s in surs):
        flag += 1
        print("  ?? %-24s %-40s | %s" % (o["bank"][:24], o["pg_title"][:40],
                                         o["pg_authors"][:44]))
print("  flagged:", flag)
