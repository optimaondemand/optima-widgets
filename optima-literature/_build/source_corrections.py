# -*- coding: utf-8 -*-
"""source_corrections.py -- typos in the source documents, corrected by hand.

The official book list (.docx) is the authority for WHICH titles are approved.
It is not authoritative on spelling, and a typo there propagates into every
generated artifact: the card, the search key, the id, the printed book list a
family buys from.

Correcting the .docx itself is the real fix and belongs with whoever owns that
document. This file exists so the generated pages are right in the meantime,
and so the list of known source typos is written down somewhere rather than
carried in somebody's head.

Rules:
  - key on the exact string as it appears in the source, so a fix that is later
    made upstream simply stops matching and this entry becomes dead weight
    rather than a second, conflicting opinion
  - one line of provenance per entry: who says it is wrong
  - corrections of FACT only -- spelling of a title, a misattributed author.
    Never a change of which titles are on the list.
"""

TITLE_FIX = {
    # Jessica, 2026-08-27: "There is no apostrophe in Federalist Paper."
    # The work is The Federalist Papers (1788); the source .docx has an
    # intrusive possessive. Open Library agrees: the edition record the
    # catalogue already resolved is titled "The Federalist papers".
    "The Federalist's Papers": "The Federalist Papers",
}

AUTHOR_FIX = {
    # (title as it appears AFTER TITLE_FIX) -> author
    # Left empty deliberately. The Federalist Papers has no author in the
    # catalogue, and the honest attribution is Alexander Hamilton, James
    # Madison and John Jay writing as "Publius" -- but adding an author is a
    # content decision, not a typo fix, so it waits for a ruling.
}


def apply_to_records(records):
    """Rewrite known source typos in place. Returns a list of what changed."""
    changed = []
    for r in records:
        old = r.get("title")
        new = TITLE_FIX.get(old)
        if new:
            r["title"] = new
            changed.append((old, new))
            # listed_as is the raw source line shown as provenance; correct the
            # title inside it too, or the card contradicts itself.
            if isinstance(r.get("listed_as"), str) and old in r["listed_as"]:
                r["listed_as"] = r["listed_as"].replace(old, new)
            rev = r.get("review")
            if isinstance(rev, dict):
                for k in ("listed_item", "title", "sheet_title"):
                    if isinstance(rev.get(k), str) and old in rev[k]:
                        rev[k] = rev[k].replace(old, new)
        who = AUTHOR_FIX.get(r.get("title"))
        if who and not r.get("author"):
            r["author"] = who
            changed.append((r["title"], "author -> " + who))
    return changed
