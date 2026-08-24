"""
match_free.py — Stage 3 of the Optima literature spine.

Decides, per record, what a teacher can get for free and how honestly it can be
offered next to the edition the book list tells them to buy.

Emits one of three states, which drive the widget's signposting:

  identical  the free text IS the assigned text. Only possible when the work is
             English-original and public domain -- Austen's words are Austen's
             words in any public-domain edition.
  similar    a free version exists but in a DIFFERENT translation or edition.
             Offered as "Get a similar version for free", never as the same book.
             Buy Fitzgerald's Odyssey, read Butler's free.
  none       no free version can be honestly offered.

THE SAFETY RULE, inherited from the Independent Reading build:
GUTENBERG IS THE COPYRIGHT TEST. Project Gutenberg only distributes US-public-
domain works, so a confident Gutenberg match IS the clearance. We never
adjudicate a title's copyright ourselves and never link a modern book to a
random "free ebook" site.

Consequence, deliberate: the six loose school-server PDFs of IN-COPYRIGHT
stories in the official book list (The Scarlet Ibis, Charles, Walter Mitty,
There Will Come Soft Rains, Death by Scrabble, Harrison Bergeron) are NOT
offered as free versions. A PDF on a school server is not a licence.

Where a work is public domain by date but has no trusted source, the state is
"none" with reason "needs_sourcing" -- an actionable gap, not a silent blank.
"""
import json, re
from pathlib import Path

import first_pub as FP

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
IR_PD_LINKS = Path(r"C:\Users\JessicaDrexel\OneDrive - OptimaEd\ELA"
                   r"\_independent-reading\_build\pd_links.json")

# Hosts we will hand to a teacher as a free source. Everything else is ignored,
# however convenient, because we cannot vouch for its rights.
TRUSTED = (
    "gutenberg.org",
    "standardebooks.org",
    "wikisource.org",
    "loc.gov",
    "folger.edu",
    "folger-main-site-assets.s3.amazonaws.com",   # Folger's own PDF host
    "gutenberg.net.au",
    "gutenberg.ca",
    "americanliterature.com",
    "state.gov",             # American English (US government)
    "fordlibrarymuseum.gov",
    "archive.org",           # only when the review sheet named it explicitly
)

# View-online-only: legitimate to LINK, never to present as a download, and
# never as evidence a work is public domain (Poetry Foundation licenses
# in-copyright poems).
VIEW_ONLY = ("poetryfoundation.org", "poets.org", "poetryverse.com")


def host_of(url):
    m = re.match(r'https?://([^/]+)', url or "")
    return (m.group(1).lower() if m else "")


def trusted(url):
    h = host_of(url)
    return any(h == t or h.endswith("." + t) for t in TRUSTED)


def view_only(url):
    h = host_of(url)
    return any(h == t or h.endswith("." + t) for t in VIEW_ONLY)


def load_ir_links():
    """
    The Independent Reading harvest: 171 confirmed Gutenberg matches keyed
    "Title|Author". Reuse rather than re-harvest -- these were already audited
    on two axes (right work, whole work).
    """
    if not IR_PD_LINKS.exists():
        print(f"!! {IR_PD_LINKS.name} not found; skipping IR reuse")
        return {}
    raw = json.loads(IR_PD_LINKS.read_text(encoding="utf8"))
    out = {}
    for k, v in raw.items():
        if not v or not v.get("url"):
            continue
        title, _, author = k.partition("|")
        out[FP_key(title, author)] = {
            "url": v["url"],
            "gid": v.get("gid"),
            "source": "gutenberg",
            "matched_title": v.get("gtitle"),
            "matched_authors": v.get("gauthors"),
            "via": "independent-reading harvest",
        }
    return out


def FP_key(title, author):
    """Mirror of parse_sources.joinkey. Kept identical on purpose."""
    t = re.sub(r'^(the|a|an)\s+', "", (title or "").lower()).strip()
    t = re.sub(r'[^a-z0-9 ]', "", t)
    t = re.sub(r'\s+', " ", t).strip()
    a = (author or "").lower()
    a = re.sub(r'[^a-z ]', " ", a)
    surname = ""
    if a.strip():
        toks = [w for w in a.split() if len(w) > 2 and w not in
                ("and", "the", "translated", "by", "trans", "edition", "library")]
        surname = toks[-1] if toks else ""
    return f"{t}|{surname}"


def translator_surname(name):
    if not name:
        return None
    toks = [w for w in re.sub(r'[^A-Za-z .]', " ", name).split()
            if len(w) > 2 and not w.endswith(".")]
    return toks[-1].lower() if toks else None


def decide(rec, ir_links):
    """Return the free-version block for one record."""
    key = rec["key"]
    review = rec.get("review") or {}
    category = review.get("category")            # PD / COPYRIGHT / PD_WORK_C_EDITION / ...
    work = FP.WORKS.get(key)
    lang = work[2] if work else None
    is_english = lang in FP.ENGLISH_ORIGINAL if lang else None

    # ---- candidate free sources, best first
    cands = []
    if key in ir_links:
        cands.append(ir_links[key])
    rurl = review.get("pd_source_url")
    if rurl and trusted(rurl):
        cands.append({"url": rurl, "source": host_of(rurl).replace("www.", ""),
                      "matched_title": review.get("pd_source_title"),
                      "via": "copyright review sheet"})
    burl = rec.get("url")
    if burl and trusted(burl):
        cands.append({"url": burl, "source": host_of(burl).replace("www.", ""),
                      "matched_title": None,
                      "via": "official book list link"})

    # A view-only link is recorded separately: linkable, not a download, and
    # never proof of public-domain status.
    read_online = None
    for u in (burl, rurl):
        if u and view_only(u):
            read_online = {"url": u, "source": host_of(u).replace("www.", "")}
            break

    free = cands[0] if cands else None

    # ---- state
    if category == "COPYRIGHT":
        # In copyright. Even a Gutenberg-looking hit would be a mismatch, so no
        # free offer is made regardless of what turned up.
        return {"state": "none", "reason": "in_copyright",
                "free": None, "read_online": read_online}

    if not free:
        if category in ("PD", "PD_WORK_C_EDITION"):
            return {"state": "none", "reason": "needs_sourcing",
                    "free": None, "read_online": read_online}
        return {"state": "none", "reason": "unknown_rights",
                "free": None, "read_online": read_online}

    # A free source exists. Is it the same text the book list points at?
    listed_translator = None
    ed = rec.get("edition") or {}
    roles = ed.get("roles") or {}
    listed_translator = roles.get("translator")
    if not listed_translator:
        hint = rec.get("edition_hint") or ""
        m = re.search(r'translat\w*\s*(?:by)?\s*(.+)$', hint, re.I)
        if m:
            listed_translator = m.group(1).strip(" .,")

    if is_english is True and not listed_translator:
        # Original-language English work: the public-domain text IS the text.
        # An edition may add apparatus, but the words are the same.
        return {"state": "identical", "reason": "english_original_pd",
                "free": free, "read_online": read_online}

    if listed_translator:
        # Translated work with a named translator on the buy side. The free
        # version is a different translation unless proven otherwise, and we
        # do not have per-source translator data for every Gutenberg edition,
        # so "similar" is the honest default.
        ls = translator_surname(listed_translator)
        tinfo = FP.TRANSLATIONS.get(ls) if ls else None
        return {"state": "similar", "reason": "different_translation",
                "free": free, "read_online": read_online,
                "listed_translator": listed_translator,
                "listed_translation_year": (tinfo or {}).get("year"),
                "note": "Free text is a different translation from the one the "
                        "book list specifies."}

    if is_english is False:
        # Translated work, no translator named anywhere on the buy side.
        return {"state": "similar", "reason": "translation_unspecified",
                "free": free, "read_online": read_online,
                "note": "Book list does not name a translator, so the free text "
                        "cannot be confirmed as the same version."}

    # No curated language for this work: PD source exists, relationship unknown.
    return {"state": "similar", "reason": "unverified_match",
            "free": free, "read_online": read_online,
            "note": "Free source found; not verified as the same edition."}


def main():
    src = DATA / "stage2_records.json"
    if not src.exists():
        src = DATA / "stage1_records.json"
        print(f"note: stage 2 output not present, using {src.name}")
    recs = json.loads(src.read_text(encoding="utf8"))
    book = recs["booklist"]
    ir = load_ir_links()
    print(f"reused {len(ir)} audited Gutenberg links from the "
          f"Independent Reading harvest\n")

    from collections import Counter
    for b in book:
        b["free_version"] = decide(b, ir)

    (DATA / "stage3_records.json").write_text(
        json.dumps(recs, indent=1, ensure_ascii=False), encoding="utf8")

    st = Counter(b["free_version"]["state"] for b in book)
    rs = Counter(b["free_version"]["reason"] for b in book)
    print("-- free-version state --")
    for k in ("identical", "similar", "none"):
        print(f"   {k:10} {st.get(k,0)}")
    print()
    print("-- reason --")
    for k, n in rs.most_common():
        print(f"   {k:26} {n}")
    print()
    print("-- 'get a similar version for free' cases (buy X, read Y) --")
    for b in book:
        fv = b["free_version"]
        if fv["state"] == "similar" and fv.get("listed_translator"):
            print(f"   G{b['grade']:>2} {b['title'][:32]:32} buy: {fv['listed_translator'][:22]:22}"
                  f" free: {fv['free']['source']}")
    print()
    print("-- public domain but NO trusted source yet (actionable gap) --")
    gaps = [b for b in book if b["free_version"]["reason"] == "needs_sourcing"]
    for b in gaps:
        print(f"   G{b['grade']:>2} {b['title'][:44]:44} | {str(b.get('author'))[:24]}")
    print(f"   ({len(gaps)} total)")

    # ---- gate
    problems = []
    for b in book:
        fv = b["free_version"]
        if fv["state"] != "none" and not fv.get("free"):
            problems.append(f"{b['title']!r}: state {fv['state']} with no free source")
        if (b.get("review") or {}).get("category") == "COPYRIGHT" and fv["free"]:
            problems.append(f"{b['title']!r}: IN COPYRIGHT but a free source was offered")
        u = (fv.get("free") or {}).get("url")
        if u and not trusted(u):
            problems.append(f"{b['title']!r}: untrusted free host {host_of(u)}")
    print()
    if problems:
        print(f"!! GATE: {len(problems)} problem(s)")
        for p in problems[:20]:
            print("   -", p)
        raise SystemExit(1)
    print("GATE: clean")


if __name__ == "__main__":
    main()
