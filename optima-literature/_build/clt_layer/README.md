# CLT Author Bank layer — how `clt_additions.py` was made

`_build/clt_additions.py` is a **frozen table**, like `clt_titles.py` and
`course_editions.py`: the build reads it directly and never recomputes it. This
folder is the pipeline that produced it, kept so the 129 records can be audited
and regenerated rather than taken on trust.

## The problem it solves

The catalogue is generated from the OAO book list, so all 226 original records
are on that list by construction. The CLT badge could therefore only mark
titles already present — 42 cards, covering **30 of the bank's 162 entries**.
The other **132 entries had no title in the library at all**.

Of those 132:

| outcome | n | what it means |
|---|---|---|
| `gutenberg` | 107 | a verified public-domain English text |
| `purchase`  | 22  | no PD English text; a real ISBN instead |
| `existing`  | 3   | already in the catalogue under an author-less record |

129 new records + 3 rulings added to `clt_titles.py` = all 162 entries covered.

## Running it

```
python match_pg.py       # selection -> Gutenberg candidates      (needs pg_catalog.csv)
python resolve_clt.py    # + manual rulings -> clt_resolved.json
python resolve_buy.py    # the 22 purchase editions -> clt_buy.json
python fix_buy.py        # read every ISBN back and verify it
python gen_additions.py  # -> ../clt_additions.py
```

`pg_catalog.csv` is **not committed** (21 MB). Re-download it from Gutenberg's
own bulk endpoint, which is the sanctioned way to query the catalogue — the
search pages explicitly ask not to be scraped:

```
https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv
```

`find.py` and `probe.py` are the lookup helpers used to confirm a work by eye:

```
python find.py "origin of species" darwin     # title search, any author
python probe.py augustine boethius            # everything PG holds for an author
```

## What is judgement and what is not

**Judgement:** which work represents each author. CLT publishes an *author*
list and never says which works appear on the exam, so `selection.py` is
Optima's editorial choice and is meant to be argued with. Same for
`shelves.py` (which shelf a title sits on) and `dates.py` (composition dates,
several of them approximate and marked `circa`).

**Not judgement:** the bibliography. Every Gutenberg id was read out of
Gutenberg's own catalogue export; every ISBN was read back from the Open
Library edition record by `fix_buy.py` before it was written down.

## Why the verification steps exist

Each one caught a real error:

- **Author-name matching produces confident nonsense.** "Jerome" matches Jerome
  K. Jerome, "Bernard" matches Bernard Shaw, "Hildegard" matches Hildegard
  Frey's Camp Fire Girls, "Anselm" matched a Confederate war history. Reading
  all 85 auto-matches by eye is what caught them.
- **A high score is not the right work.** Darwin resolved to his 1842/44
  foundational essays rather than *On the Origin of Species*; Bunyan to a
  one-syllable adaptation by Lucy Aikin; Wollstonecraft to the *Posthumous
  Works*. All three scored well.
- **A title search is not a verification.** Open Library returns Steinbeck's
  *The Pearl* for "Pearl" by "Anonymous", and it passes any keyword check
  looking for the word "pearl". `fix_buy.py` reads the edition record back.
- **Gutenberg's language column is multi-valued.** Wittgenstein's *Tractatus*
  is `de; en`; an `en`-only filter silently drops it.
- **Three bank entries were already in the catalogue** under records with an
  empty author field, so no surname existed to match: *Confucian Analects*,
  the Nietzsche excerpts, and the *Federalist Papers*. Found by listing the
  author-less records, not by matching. They are badged in `clt_titles.py`;
  duplicating them as new cards would have been the easy wrong answer.

## Invariants the gate enforces

`build_reference_library.gate()` fails the build if a CLT-layer title is ever
marked taught, claims a book-list line, loses its CLT badge, goes unshelved,
carries a non-Gutenberg free link, or is purchase-only with no ISBN — and if
any bank entry ends up with no title at all.
