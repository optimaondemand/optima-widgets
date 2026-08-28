# -*- coding: utf-8 -*-
"""Add the CLT Author Bank layer to library.json, surgically.

WHY NOT JUST RE-RUN build_manifest.py
-------------------------------------
A full regeneration rewrites all 226 book-list records from stage3, and doing
that today produces 55 lines of drift that have nothing to do with this change
(genres.py renamed its fallback shelf "Unshelved" -> "Unclassified" after
library.json was last written). That regeneration is a deliberate decision on
its own, not a side effect of adding titles -- so this script leaves every
existing record byte-for-byte alone and only appends.

It is re-runnable: CLT records are keyed by id and replaced in place, never
duplicated. Run it after build_reference_library.py.
"""
import json
from pathlib import Path

import build_reference_library as BRL
import clt_additions as CA

ROOT = Path(__file__).resolve().parent.parent
LIB = ROOT / "library.json"

CLT_SOURCE = {
    "role": "CLT Author Bank",
    "path": "https://www.cltexam.com/tests/authors/",
    "authority": ("CLT publishes the AUTHOR list only, never the works. Which "
                  "work represents each author is Optima's editorial choice; "
                  "see _build/clt_additions.py"),
}


def rec_for_clt(b):
    """library.json shape for one CLT record, mirroring build_manifest.rec_for."""
    BRL.enrich_clt(b)
    fv = b.get("free_version") or {}
    free = fv.get("free") or {}
    ed = b.get("edition") or {}
    return {
        "id": "clt-" + BRL.slug(b["title"])[:44],
        "title": b["title"],
        "author": b.get("author"),
        "authors": None,
        "grade": None,               # on no grade list, and must not read as one
        "form": None,
        "shelf": b["_shelf"],
        "shelf_source": b["_shelf_src"],
        "listed_as": None,           # not on the OAO book list
        "listed_twice_in_source": False,
        "first_published": ({
            "year": b["_year_num"], "circa": bool(b.get("clt_circa")),
            "language": b["_lang"], "confidence": "high", "note": None,
        } if b["_year_num"] is not None else None),
        "buy": {
            "isbn": b["_isbn"],
            "isbn_is_real": bool(b["_isbn"] and b["_isbn"][:1].isdigit()),
            "edition_title": b["_edition_title"],
            "translator": None, "editor": None, "illustrator": None,
            "reteller": None,
            "publisher": b["_publisher"],
            "edition_year": b["_edition_year"],
            "pages": None,
            "url": b.get("url"),
            "url_kind": b.get("url_kind"),
            "edition_hint_from_booklist": None,
        },
        "free": {
            "state": fv.get("state"), "reason": fv.get("reason"),
            "url": free.get("url") or None,
            "source": free.get("source") or None,
            "gutenberg_id": free.get("gutenberg_id"),
            "matched_title": free.get("matched_title"),
            "via": free.get("via"), "note": fv.get("note"),
        },
        "read_online": None,
        "flags": {"translation": "none", "translation_year": None,
                  "verify": False},
        "taught": None,              # no Optima course assigns a CLT title
        "prior_review": None,
        "clt": {
            "bank_entry": b["clt_bank_entry"],
            "on_oao_book_list": False,
            "note": ("Present because CLT draws passages from this author. "
                     "CLT does not publish which works appear."),
        },
    }


def main():
    doc = json.loads(LIB.read_text(encoding="utf8"))
    titles = doc["titles"]
    before = len(titles)

    new = [rec_for_clt(dict(r)) for r in CA.ADDITIONS]
    byid = {r["id"]: r for r in new}
    if len(byid) != len(new):
        raise SystemExit("CLT records collide on id")

    kept = [t for t in titles if not str(t.get("id", "")).startswith("clt-")]
    if len(kept) != 226:
        raise SystemExit(f"expected 226 book-list records, found {len(kept)}")
    doc["titles"] = kept + new

    if not any(s.get("role") == CLT_SOURCE["role"] for s in doc["sources"]):
        doc["sources"].append(CLT_SOURCE)

    c = doc["counts"]
    c["titles"] = len(doc["titles"])
    c["on_oao_book_list"] = len(kept)
    c["clt_author_bank_layer"] = len(new)
    # library.json is generated WITHOUT source_corrections (build_manifest does
    # not apply them), so it still stores "The Federalist's Papers". The CLT
    # ruling is keyed on the corrected title, as the page uses it. Correct the
    # title for the lookup only -- never rewrite the stored generated value.
    import source_corrections as SC
    c["clt_badged_total"] = sum(
        1 for t in doc["titles"]
        if t.get("clt")
        or BRL.CT.is_clt(t.get("grade"),
                         SC.TITLE_FIX.get(t["title"], t["title"])))
    c["free_same_text"] = sum(1 for t in doc["titles"]
                              if t["free"]["state"] == "identical")
    c["free_similar_version"] = sum(1 for t in doc["titles"]
                                    if t["free"]["state"] == "similar")
    c["must_purchase"] = sum(1 for t in doc["titles"]
                             if t["free"]["state"] == "none")

    LIB.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf8")
    print("library.json: %d -> %d records (+%d CLT)"
          % (before, len(doc["titles"]), len(new)))
    print("  counts:", {k: c[k] for k in
                        ("titles", "on_oao_book_list", "clt_author_bank_layer",
                         "clt_badged_total", "free_same_text",
                         "free_similar_version", "must_purchase")})


if __name__ == "__main__":
    main()
