# -*- coding: utf-8 -*-
"""
build_manifest.py — emits library.json, the canonical export.

This file is the CONTRACT between optima-literature (content) and
optima-widgets (presentation). Both the teacher ELA Reference Library and the
student Independent Reading library are generated from it, so the two can never
disagree about a title's rights, edition, or shelf.

Consumers read library.json. They do not read the three source documents, and
they do not re-derive rights. If a fact is wrong, it is wrong here and gets
fixed once.

Every field is either sourced or explicitly null. Nothing is inferred to fill a
gap: an unknown translator is null, not a guess, because the whole purpose of
these columns is that somebody can act on them.
"""
import json
from collections import Counter
from datetime import date
from pathlib import Path

import course_editions as CE
import first_pub as FP
import genres as G
import build_reference_library as BRL

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "library.json"

SCHEMA = 1

SOURCES = [
    {"role": "official book list",
     "path": r"OneDrive - OptimaEd\ELA\Book List 2026-27 (1).docx",
     "authority": "what a family may buy; NOT a rights document"},
    {"role": "copyright review",
     "path": r"OneDrive - OptimaEd\Claude's Playground\ELA"
             r"\master_book_list_copyright_review (1).xlsx",
     "authority": "prior triage, prepared 2026-04-30; contains known errors, "
                  "see open_questions"},
    {"role": "course editions",
     "path": r"_build\course_editions.py",
     "authority": "AUTHORITATIVE. The edition each course actually teaches, "
                  "audited from the coursework 2026-08-20/21"},
    {"role": "bibliographic resolution",
     "path": "Open Library (openlibrary.org)",
     "authority": "exact edition, publisher, translator/editor by ISBN. Google "
                  "Books not used: HTTP 429, shared quota exhausted"},
    {"role": "free-text clearance",
     "path": "Project Gutenberg via the Independent Reading harvest",
     "authority": "Gutenberg distributes only US-public-domain works, so a "
                  "confident match IS the clearance"},
]

# Errors found in the copyright review sheet while building this. Carried in the
# manifest so consumers know not to trust those rows, and so the corrections
# survive even if this session's notes do not.
KNOWN_REVIEW_ERRORS = [
    {"title": "Their Eyes Were Watching God", "grade": "10",
     "sheet_says": "PD, via Standard Ebooks",
     "actually": "In US copyright until 2033. Standard Ebooks does not host it.",
     "severity": "high"},
    {"title": "The Most Dangerous Game", "grade": "7",
     "sheet_says": "Copyrighted - use licensed copy only",
     "actually": "US public domain since 1 Jan 2020. Contradicts the sheet's "
                 "own stated pre-1931 rule.",
     "severity": "medium"},
    {"title": "The Sniper", "grade": "9",
     "sheet_says": "Copyrighted - use licensed copy only",
     "actually": "US public domain since 1 Jan 2019 (published 1923).",
     "severity": "medium"},
    {"title": "Electra", "grade": "9",
     "sheet_says": "Public domain",
     "actually": "Sophocles is PD; the LISTED edition is E. F. Watling's "
                 "translation, (c) 1953 and in copyright.",
     "severity": "medium"},
    {"title": "Do Not Go Gentle into That Good Night", "grade": "6",
     "sheet_says": 'rights holder "Elie Wiesel estate"',
     "actually": "Dylan Thomas / New Directions. Verdict is right, the holder "
                 "field is a copy-paste error.",
     "severity": "low"},
]

OPEN_QUESTIONS = [
    {"q": "Sir Gawain and the Green Knight - which translation is in the "
          "9th-grade folder?",
     "why": "89pp of body text with no title page, copyright page, or credit. "
            "Not Tolkien, Armitage, or Borroff by their openings. Until it is "
            "named, the coursework's public-domain claim is unverifiable.",
     "blocks": "a rights claim in live coursework"},
    {"q": "The Qur'an, Suras 1 and 112 - which English translation?",
     "why": "12th-grade page says only 'Public domain English text'. Rodwell "
            "(1861) would be PD; Yusuf Ali (1934) would not.",
     "blocks": "a rights claim in live coursework"},
    {"q": "Plato, Allegory of the Cave - which translation?",
     "why": "12th-grade page says only 'Public domain English text. Excerpt.'",
     "blocks": "a rights claim in live coursework"},
    {"q": "Aristotle, Poetics (10th Honors) - which translation?",
     "why": "No credit line found anywhere in the built lesson.",
     "blocks": "a rights claim in live coursework"},
    {"q": "D. P. Chase's Nicomachean Ethics - 1847 or the 1877 revision?",
     "why": "1847 trips the pre-1850 ARCHAIC flag; 1877 lands in OLDER. This "
            "is the only live Optima translation on the wrong side of that "
            "line, so the tier depends on it.",
     "blocks": "the accuracy of one flag"},
    {"q": "Add Perseus (Tufts) to the trusted free-source allowlist?",
     "why": "Perseus is Electra's only free source and is a serious academic "
            "library, but adding it means vouching for a source rather than "
            "letting Gutenberg be the test.",
     "blocks": "one free link"},
    {"q": "Shelve the 43 unshelved titles?",
     "why": "Mostly K-5 picture books the student library never carried, so no "
            "shelf could be harvested. Genre filtering is degraded for those.",
     "blocks": "nothing; cosmetic"},
]


def rec_for(b):
    fv = b.get("free_version") or {}
    free = fv.get("free") or {}
    ro = fv.get("read_online") or {}
    ed = b.get("edition") or {}
    work = b.get("_work")
    c = b.get("_course")
    review = b.get("review") or {}

    return {
        "id": f'{b["grade"]}-{BRL.slug(b["title"])[:44]}',
        "title": b["title"],
        "author": b.get("author"),
        "authors": b.get("authors"),
        "grade": b["grade"],
        "form": b.get("kind"),
        "shelf": b["_shelf"],
        "shelf_source": b["_shelf_src"],
        "listed_as": b.get("listed_as"),
        "listed_twice_in_source": b.get("listed_count", 1) > 1,

        "first_published": ({
            "year": work[0], "circa": work[1], "language": work[2],
            "confidence": work[3], "note": work[4],
        } if work else None),

        "buy": {
            "isbn": b["_isbn"],
            "isbn_is_real": bool(b["_isbn"] and b["_isbn"][:1].isdigit()),
            "edition_title": b["_edition_title"],
            "translator": b["_translator"],
            "editor": b["_editor"],
            "illustrator": b["_illustrator"],
            "reteller": b["_reteller"],
            "publisher": b["_publisher"],
            "edition_year": b["_edition_year"],
            "pages": b["_pages"],
            "url": b.get("url"),
            "url_kind": b.get("url_kind"),
            "edition_hint_from_booklist": b.get("edition_hint"),
        },

        "free": {
            "state": fv.get("state"),
            "reason": fv.get("reason"),
            "url": free.get("url") or None,
            "source": free.get("source") or None,
            "gutenberg_id": free.get("gid"),
            "matched_title": free.get("matched_title"),
            "via": free.get("via"),
            "note": fv.get("note"),
        },
        "read_online": ({"url": ro["url"], "source": ro.get("source"),
                         "download": False} if ro.get("url") else None),

        "flags": {
            "translation": b["_flag"],
            "translation_year": b["_translation_year"],
            "verify": bool(b["_verify"]),
        },

        "taught": ({
            "grade": c["grade"], "used": c["used"], "edition": c.get("edition"),
            "stored_file_ok": c.get("stored_ok"), "note": c.get("note"),
            "verify": c.get("verify"),
        } if c else None),

        "prior_review": {
            "category": review.get("category"),
            "holder": review.get("holder"),
            "caution": review.get("caution"),
            "trust": "low - see known_review_errors",
        } if review else None,
    }


def main():
    src = DATA / "stage3_records.json"
    if not src.exists():
        raise SystemExit("run match_free.py first")
    recs = json.loads(src.read_text(encoding="utf8"))
    book = BRL.enrich(recs["booklist"])
    book.sort(key=BRL.sort_key)

    titles = [rec_for(b) for b in book]

    st = Counter(t["free"]["state"] for t in titles)
    payload = {
        "schema": SCHEMA,
        "name": "Optima literature corpus",
        "purpose": "Canonical record of every text in Optima curriculum: what it "
                   "costs, what is free, which edition, and who translated it. "
                   "Serves multiple widgets; consumers must not re-derive rights.",
        "generated": date.today().isoformat(),
        "sources": SOURCES,
        "counts": {
            "titles": len(titles),
            "free_same_text": st.get("identical", 0),
            "free_similar_version": st.get("similar", 0),
            "must_purchase": st.get("none", 0),
            "taught_in_a_course": sum(1 for t in titles if t["taught"]),
            "translators_named": sum(1 for t in titles if t["buy"]["translator"]),
            "isbns_resolved": sum(1 for t in titles if t["buy"]["isbn_is_real"]),
            "needing_verification": sum(1 for t in titles if t["flags"]["verify"]),
        },
        "signposting": {
            "identical": BRL.STATE_BLURB["identical"],
            "similar": BRL.STATE_BLURB["similar"],
            "none": BRL.STATE_BLURB["none"],
            "archaic": BRL.FLAG_TITLE["archaic"],
            "older": BRL.FLAG_TITLE["older"],
            "rule": "A translation flag is NEVER applied to a work written in "
                    "English, however old; there the old English is the text.",
        },
        "titles": titles,
        "taught_but_on_no_list": [
            {"title": t, "author": a, "grade": g, "note": n}
            for t, a, g, n in CE.NOT_ON_BOOKLIST
        ],
        "known_review_errors": KNOWN_REVIEW_ERRORS,
        "open_questions": OPEN_QUESTIONS,
    }

    # ---- gate
    problems = []

    # A curated table is keyed by hand, so a typo does not error -- it silently
    # drops the entry and the widget shows a blank field that looks like missing
    # data rather than a bug. Ten of these were real. Fail the build instead.
    corpus_keys = {b["key"] for b in book}
    for label, tbl in (("course_editions.COURSE", CE.COURSE),
                       ("first_pub.WORKS", FP.WORKS)):
        orphans = [k for k in tbl if k not in corpus_keys]
        for k in orphans:
            problems.append(f"{label}: key matches no title in the corpus: {k!r}")

    ids = [t["id"] for t in titles]
    for k, n in Counter(ids).items():
        if n > 1:
            problems.append(f"duplicate id: {k}")
    for t in titles:
        if t["free"]["state"] not in ("identical", "similar", "none"):
            problems.append(f'{t["title"]!r}: bad free state {t["free"]["state"]!r}')
        if t["free"]["state"] != "none" and not t["free"]["url"]:
            problems.append(f'{t["title"]!r}: {t["free"]["state"]} with no url')
        if t["flags"]["translation"] in ("archaic", "older"):
            lang = (t["first_published"] or {}).get("language")
            if lang in FP.ENGLISH_ORIGINAL:
                problems.append(f'{t["title"]!r}: translation flag on English original')
    if problems:
        print(f"!! GATE: {len(problems)} problem(s)")
        for p in problems[:20]:
            print("   -", p)
        raise SystemExit(1)

    OUT.write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf8")
    kb = OUT.stat().st_size / 1024
    print(f"wrote {OUT.name}  ({kb:.0f} KB)")
    for k, v in payload["counts"].items():
        print(f"   {k:24} {v}")
    print(f"   {'known review errors':24} {len(KNOWN_REVIEW_ERRORS)}")
    print(f"   {'open questions':24} {len(OPEN_QUESTIONS)}")


if __name__ == "__main__":
    main()
