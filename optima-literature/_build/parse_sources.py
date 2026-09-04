"""
parse_sources.py — Stage 1 of the Optima literature spine.

Reads the three authorities and emits one normalised record per listed item:

  A. Official Master Book List 2026-27 (.docx)  -> what teachers may choose, + purchase links
  B. master_book_list_copyright_review (.xlsx)  -> prior rights triage (has known errors)
  C. course_editions.py                        -> the edition ACTUALLY taught (authoritative)

Output: data/stage1_records.json  +  a human-readable report on stdout.

Nothing here decides rights. This stage only gathers and joins. Verdicts are
stage 3, after ISBN resolution, so that a verdict is never recorded without the
edition it applies to.
"""
import json, re, zipfile, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data"
OUT.mkdir(exist_ok=True)

DOCX = Path(r"C:\Users\JessicaDrexel\OneDrive - OptimaEd\ELA\Book List 2026-27 (1).docx")
XLSX = Path(r"C:\Users\JessicaDrexel\OneDrive - OptimaEd\Claude's Playground\ELA"
            r"\master_book_list_copyright_review (1).xlsx")

GRADE_RE = re.compile(r'^\s*Grade\s*(K|\d{1,2})\s*:?\s*$', re.I)
GRADE_INLINE_RE = re.compile(r'^\s*Grade\s*(K|\d{1,2})\s*:?\s+(.*)$', re.I)

# "Poem: ", "Short Story: ", "Novel: ", "Play: ", "Collection of short stories: "
KIND_PREFIX = re.compile(
    r'^\s*(Poem Connection|Poem|Short Story|Short stories|Novel|Play|'
    r'Collection of short stories|Connection text\s*\(speech\)|Connection text|'
    r'Poetry|Supplementary Texts?)\s*:\s*',
    re.I)

KIND_MAP = {
    "poem": "poem", "poem connection": "poem", "poetry": "poem",
    "short story": "short story", "short stories": "short story",
    "collection of short stories": "short story collection",
    "novel": "novel", "play": "play",
    "connection text (speech)": "speech", "connection text": "speech",
}

# Edition / translation signals that appear inline in the listed line.
EDITION_HINT = re.compile(
    r'((?:translated|translation|trans\.)\s*(?:by)?\s*[^,;\[\]]{2,60}'
    r'|Folger\s+Shakespeare\s+Library\s+Edition'
    r'|Dover\s+Thrift[^,;]*'
    r'|Penguin\s+Classics?[^,;]*'
    r'|Epic\s+Version)', re.I)

NOISE_PREFIXES = (
    "teachers choose", "teacher will provide", "focus:", "novels &", "novels and",
    "in addition to the core", "books that are used", "supplementary texts",
)


def clean(s: str) -> str:
    """Normalise the smart punctuation the docx is full of."""
    if not s:
        return ""
    s = (s.replace("\u2019", "'").replace("\u2018", "'")
           .replace("\u201c", '"').replace("\u201d", '"')
           .replace("\u2013", "-").replace("\u2014", "-")
           .replace("\u00a0", " ").replace("\ufeff", ""))
    s = re.sub(r"&amp;", "&", s)
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()


def norm_grade(raw: str) -> str:
    raw = raw.strip().upper()
    return "K" if raw == "K" else str(int(raw))


# ---------------------------------------------------------------- A. the .docx

def read_docx_lines():
    """Yield (text, [urls]) per paragraph, with hyperlink targets preserved."""
    z = zipfile.ZipFile(DOCX)
    xml = z.read("word/document.xml").decode("utf8", "replace")
    rels = dict(re.findall(r'Id="([^"]+)"[^>]*?Target="([^"]+)"',
                           z.read("word/_rels/document.xml.rels").decode("utf8", "replace")))

    # Tag each hyperlink run so the URL survives tag-stripping.
    def hl(m):
        rid = m.group(1)
        inner = re.sub(r"<[^>]+>", "", m.group(0))
        url = rels.get(rid, "")
        return f"{inner}\x00{url}\x00"

    xml = re.sub(r'<w:hyperlink[^>]*r:id="([^"]+)"[^>]*>.*?</w:hyperlink>',
                 hl, xml, flags=re.S)
    xml = xml.replace("</w:p>", "\n@@P@@")
    text = re.sub(r"<[^>]+>", "", xml)

    for para in text.split("@@P@@"):
        urls = re.findall(r"\x00([^\x00]*)\x00", para)
        body = clean(re.sub(r"\x00[^\x00]*\x00", "", para))
        if body:
            yield body, [u for u in urls if u.startswith("http")]


# Lines written "Author, Work" rather than "Title, Author". The grade-12 ancient
# block is all of this shape, so a comma-split would invert title and author.
AUTHOR_FIRST = {
    "plato", "aristotle", "sophocles", "virgil", "homer", "dante alighieri",
    "nietzsche", "marcus aurelius", "confucius",
}

# Works with no author on the line at all (scripture, anonymous, collections).
NO_AUTHOR = {
    "the bible", "bhagavad gita", "the qur'an", "the quran", "buddhist parables",
    "confucian analects", "nursery rhymes", "sir gawain & the green knight",
    "sir gawain and the green knight", "the federalist's papers",
    "the federalist papers", "beowulf",
}


def split_title_author(line: str):
    """
    Listed lines are inconsistent. Handle the shapes that actually occur:
        Title by Author              "Title" by Author
        Title, Author                Author, Work        (grade-12 ancient block)
        Title by Author, <edition>   Title (no author)
        Title by Author - thematic tail
    """
    s = line.strip()

    edition = None
    m = EDITION_HINT.search(s)
    if m:
        edition = clean(m.group(1)).rstrip(".,;")

    # A leading quoted span is the title, whole and entire. This is the only
    # reliable read of 'Death by Scrabble" by Charlie Fish', where splitting on
    # the first "by" lands inside the title.
    quoted = re.match(r'^\s*"([^"]{2,90})"\s*(.*)$', s)
    if quoted:
        qtitle, rest = quoted.group(1).strip(), quoted.group(2).strip()
        a = None
        if re.match(r'^by\b', rest, re.I):
            a = re.sub(r'^by\b', "", rest, flags=re.I).strip(' ",;.')
        notes = re.findall(r'[\[(]([^\])]{1,60})[\])]', rest)
        if a:
            a = re.sub(r'\s*[\[(][^\])]*[\])]\s*', " ", a).strip(' ",;.')
            a = re.split(r'\s+-\s+', a)[0].strip(' ",;.')
        return qtitle, (a or None), edition, notes

    # Trailing bracketed notes: [excerpts], (optional), (Selected)
    notes = re.findall(r'[\[(]([^\])]{1,60})[\])]', s)
    s = re.sub(r'\s*[\[(][^\])]{1,60}[\])]\s*$', "", s).strip()
    # Unclosed parenthetical, e.g. "(select chapters: On the Rainy River, ..."
    s = re.sub(r'\s*\([^)]{0,90}$', "", s).strip()

    # Thematic tail after a dash, grade 12: "Frankenstein by Mary Shelley - Romanticism, ..."
    # Strip whenever the tail carries no "by"; a real subtitle would not sit
    # after a spaced dash on these lines.
    if re.search(r'\s+-\s+', s):
        head, tail = re.split(r'\s+-\s+', s, maxsplit=1)
        if not re.search(r'\bby\b', tail, re.I) and head.strip():
            s = head.strip()

    s = s.strip(' -,;')

    author = None
    if re.search(r'\bby\b', s, re.I):
        parts = re.split(r'\bby\b', s, maxsplit=1, flags=re.I)
        title, author = parts[0].strip(' ",'), parts[1].strip(' ",')
    elif "," in s:
        left, right = [p.strip(' ",') for p in s.split(",", 1)]
        if left.lower() in AUTHOR_FIRST:
            title, author = right, left          # "Plato, Republic"
        else:
            title, author = left, right          # "Electra, Sophocles"
    else:
        title = s.strip(' ",')

    # Strip the edition word BEFORE the no-author test, or "Beowulf translation"
    # fails to match "beowulf" in NO_AUTHOR and wrongly keeps Heaney as author.
    title = re.sub(r'\s+(translation|translated|trans\.?)$', "", title,
                   flags=re.I).strip()

    if title.lower().strip() in NO_AUTHOR:
        author = None

    # Author field frequently carries the edition hint too; peel it off.
    if author:
        m2 = EDITION_HINT.search(author)
        if m2:
            edition = edition or clean(m2.group(1)).rstrip(".,;")
            author = EDITION_HINT.sub("", author).strip(" ,;")
        # "Author: Kathryn Knight , Illustrator: Ezra Tucker available on Epic"
        if re.search(r'\b(author|illustrator)\s*:', author, re.I):
            am = re.search(r'author\s*:\s*([^,;]{2,40})', author, re.I)
            im = re.search(r'illustrator\s*:\s*([^,;]{2,40})', author, re.I)
            if im:
                edition = edition or f"illustrated by {clean(im.group(1)).strip()}"
            author = clean(am.group(1)).strip() if am else None
        if author:
            author = re.sub(r'\bavailable on\b.*$', "", author, flags=re.I)
            author = re.sub(r'^(and|&)\s+', "", author).strip(" ,;.")

    title = re.sub(r'^["\']|["\']$', "", title).strip(" ,;.")
    # "Beowulf translation by Seamus Heaney" -> the word belongs to the edition
    # hint, not the title.
    title = re.sub(r'\s+(translation|translated|trans\.?)$', "", title, flags=re.I).strip()
    return title, (author or None), edition, notes


def split_multi_author(author):
    """
    Grade 12 lists two survey lines naming several authors with no single work
    ("Short stories by Joyce, Gilman, Lawrence, Mansfield"). Returns
    (single_author, authors_list) — the list is None unless this is a survey line.

    Shared by BOTH source parsers on purpose: applying it to only one side makes
    the join keys diverge, which is exactly the bug this replaced.
    """
    if not author or author.count(",") < 2:
        return author, None
    parts = [clean(p).strip(" .;") for p in re.split(r',|\band\b', author)]
    parts = [p for p in parts if 2 < len(p) < 40]
    if len(parts) >= 3:
        return None, parts
    return author, None


ASIN_PATTERNS = [
    re.compile(r'/dp/([A-Z0-9]{10})(?:[/?]|$)'),
    re.compile(r'/ASIN/([A-Z0-9]{10})(?:[/?]|$)'),
    re.compile(r'/gp/product/([A-Z0-9]{10})(?:[/?]|$)'),
]


def extract_asin(url: str):
    for pat in ASIN_PATTERNS:
        m = pat.search(url)
        if m:
            return m.group(1)
    return None


def classify_url(url: str) -> str:
    u = url.lower()
    if "a.co/" in u:
        return "amazon_short"
    if "amazon." in u:
        # A search URL carries no ASIN and never will; it has to be resolved by
        # title instead. Distinguishing it stops the gate crying wolf.
        if re.search(r'/s\?|/s/|[?&]k=', u):
            return "amazon_search"
        return "amazon"
    if "gutenberg" in u:
        return "gutenberg"
    if "wikisource" in u:
        return "wikisource"
    if "standardebooks" in u:
        return "standard_ebooks"
    if "poetryfoundation" in u or "poetryverse" in u or "poetry.com/" in u:
        return "poetry_site"
    if "folger" in u:
        return "folger"
    if "loc.gov" in u or "guides.loc.gov" in u:
        return "loc"
    if u.endswith(".pdf"):
        return "loose_pdf"
    return "other"


def parse_booklist():
    records, grade = [], None
    for body, urls in read_docx_lines():
        m = GRADE_RE.match(body)
        if m:
            grade = norm_grade(m.group(1))
            continue
        mi = GRADE_INLINE_RE.match(body)
        if mi and len(mi.group(2)) < 3:
            grade = norm_grade(mi.group(1))
            continue
        if grade is None:
            continue
        low = body.lower()
        if any(low.startswith(p) for p in NOISE_PREFIXES):
            continue
        if len(body) < 4:
            continue
        # A bare URL on its own line is a supplementary link for the entry
        # above it (the LOC Federalist full text), not a separate work.
        if body.startswith("http"):
            if records:
                records[-1].setdefault("extra_urls", []).append(body)
            continue

        kind = None
        km = KIND_PREFIX.match(body)
        line = body
        if km:
            kind = KIND_MAP.get(km.group(1).strip().lower())
            line = KIND_PREFIX.sub("", body)

        title, author, edition, notes = split_title_author(line)
        if not title:
            continue

        author, authors = split_multi_author(author)
        if authors:
            kind = kind or "multi-author collection"

        url = urls[0] if urls else None
        records.append({
            "grade": grade,
            "listed_as": body,
            "title": title,
            "author": author,
            "authors": authors,
            "kind": kind,
            "edition_hint": edition,
            "notes": notes,
            "url": url,
            "url_kind": classify_url(url) if url else None,
            "asin": extract_asin(url) if url else None,
            "extra_urls": urls[1:] if len(urls) > 1 else [],
        })
    return records


# ---------------------------------------------------------------- B. the .xlsx

CATEGORY_SHORT = {
    "Public domain in the U.S. (or public-domain version identified)": "PD",
    "Copyrighted - use licensed copy only": "COPYRIGHT",
    "Copyrighted listed edition/translation; public-domain underlying work available": "PD_WORK_C_EDITION",
    "Copyrighted/unclear in U.S. - use licensed copy only": "UNCLEAR",
    "Mixed / item-level review needed": "MIXED",
}


def parse_review():
    try:
        import openpyxl
    except ImportError:
        print("!! openpyxl missing - skipping review sheet", file=sys.stderr)
        return []
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    ws = wb["Copyright Review"]
    rows = list(ws.iter_rows(values_only=True))
    out = []
    for r in rows[1:]:
        if not r or not r[1]:
            continue
        gm = re.match(r'Grade\s*(K|\d{1,2})', str(r[1]).strip(), re.I)
        if not gm:
            continue
        pd_title = str(r[7] or "")
        if "No safe public-domain" in pd_title:
            pd_title, pd_url = None, None
        else:
            pd_url = str(r[8] or "") or None
        # Normalise the review sheet's own listed_item through the SAME parser
        # used on the docx. Its "Parsed title" column keeps the "Poem:" /
        # "Short Story:" prefixes and smart quotes, so trusting it makes the
        # keys unjoinable by construction.
        listed = clean(str(r[2] or ""))
        line = KIND_PREFIX.sub("", listed)
        rtitle, rauthor, _redition, _rnotes = split_title_author(line)
        if not rtitle:
            rtitle = clean(str(r[3] or ""))
            rauthor = clean(str(r[4] or "")) or None
        rauthor, rauthors = split_multi_author(rauthor)

        out.append({
            "authors": rauthors,
            "grade": norm_grade(gm.group(1)),
            "listed_item": listed,
            "title": rtitle,
            "author": rauthor,
            "sheet_title": clean(str(r[3] or "")),
            "sheet_author": clean(str(r[4] or "")) or None,
            "category_raw": str(r[5] or ""),
            "category": CATEGORY_SHORT.get(str(r[5] or "").strip(), "UNKNOWN"),
            "holder": clean(str(r[6] or "")) or None,
            "pd_source_title": clean(pd_title) if pd_title else None,
            "pd_source_url": pd_url,
            "caution": clean(str(r[9] or "")) or None,
        })
    return out


# ------------------------------------------------------------------- the join

def joinkey(title, author):
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


def recover_missing_authors(book):
    """
    A few source lines omit "by": "A Christmas Carol Charles Dickens".
    The author ends up glued to the title. Rather than special-case titles,
    use the corpus itself: if an author-less title ENDS WITH a person named as
    an author elsewhere in the same book list, split there.

    Corpus-driven, so it needs no maintenance and cannot invent a name that is
    not already attested in the source document.

    Applied to BOTH source lists from a shared author pool. Fixing one side only
    changes its join key and silently orphans the row -- the same mistake the
    multi-author survey lines caused earlier.
    """
    return _recover(book, known_authors(book))


def known_authors(*record_lists):
    """Every personal name attested as an author anywhere in the sources."""
    known = {}
    for recs in record_lists:
        for b in recs:
            a = (b.get("author") or "").strip()
            if 4 < len(a) < 40 and " " in a:
                known[a.lower()] = a
    return known


def _recover(book, known):
    fixed = []
    for b in book:
        if b.get("author") or b.get("authors"):
            continue
        t = b["title"]
        low = t.lower()
        for cand_low, cand in known.items():
            if low.endswith(" " + cand_low) and len(t) > len(cand) + 3:
                b["title"] = t[: -(len(cand) + 1)].strip(" ,;.")
                b["author"] = cand
                fixed.append((t, b["title"], cand))
                break
    return fixed


def dedupe(book):
    """
    The source docx lists a few titles twice inside one grade (Number the Stars
    in G4, St. George in G6). Collapse them, keep the richer record, and record
    that the duplication is in the source rather than silently dropping it.
    """
    seen, out, collapsed = {}, [], []
    for b in book:
        k = (b["grade"], joinkey(b["title"], b["author"]))
        if k in seen:
            prev = seen[k]
            prev["listed_count"] = prev.get("listed_count", 1) + 1
            # keep whichever record carries a link
            if not prev.get("url") and b.get("url"):
                prev["url"], prev["url_kind"], prev["asin"] = (
                    b["url"], b["url_kind"], b["asin"])
            collapsed.append(k)
            continue
        b["listed_count"] = 1
        seen[k] = b
        out.append(b)
    return out, collapsed


def main():
    book = parse_booklist()
    review = parse_review()
    pool = known_authors(book, review)
    recovered = _recover(book, pool)
    recovered += _recover(review, pool)
    book, collapsed = dedupe(book)
    if recovered:
        print(f"-- recovered {len(recovered)} author(s) from glued title lines --")
        for old, newt, a in recovered:
            print(f"   {old[:44]:44} -> {newt[:30]:30} by {a}")
        print()

    rev_by_key, rev_by_grade_title = {}, {}
    for r in review:
        rev_by_key[joinkey(r["title"], r["author"])] = r
        rev_by_grade_title.setdefault(
            (r["grade"], joinkey(r["title"], r["author"])), r)

    matched = 0
    for b in book:
        k = joinkey(b["title"], b["author"])
        r = rev_by_grade_title.get((b["grade"], k)) or rev_by_key.get(k)
        b["key"] = k
        b["review"] = r
        if r:
            matched += 1

    (OUT / "stage1_records.json").write_text(
        json.dumps({"booklist": book, "review": review}, indent=1, ensure_ascii=False),
        encoding="utf8")

    # ------------------------------------------------------------- report
    from collections import Counter
    print(f"BOOKLIST entries parsed : {len(book)}")
    print(f"REVIEW rows parsed      : {len(review)}")
    print(f"joined to a review row  : {matched}/{len(book)}"
          f"  ({len(book)-matched} unmatched)")
    print()
    print("-- entries per grade --")
    for g, n in sorted(Counter(b["grade"] for b in book).items(),
                       key=lambda x: (x[0] != "K", x[0].isdigit() and int(x[0]) or 0)):
        print(f"   Grade {g:>2}: {n}")
    print()
    print("-- link target types --")
    for k, n in Counter(b["url_kind"] or "NO LINK" for b in book).most_common():
        print(f"   {k:16} {n}")
    print()
    asins = [b for b in book if b["asin"]]
    shorts = [b for b in book if b["url_kind"] == "amazon_short"]
    print(f"ASIN/ISBN extracted directly : {len(asins)}")
    print(f"a.co shorteners to resolve   : {len(shorts)}")
    print(f"no link at all               : {sum(1 for b in book if not b['url'])}")
    print()
    print("-- review verdict spread (all grades) --")
    for k, n in Counter(r["category"] for r in review).most_common():
        print(f"   {k:20} {n}")
    print()
    print("-- edition hints captured from the listed line --")
    for b in book:
        if b["edition_hint"]:
            print(f"   G{b['grade']:>2} {b['title'][:42]:42} | {b['edition_hint'][:46]}")
    print()
    print("-- UNMATCHED booklist entries (no review row) --")
    unmatched = [b for b in book if not b["review"]]
    for b in unmatched:
        print(f"   G{b['grade']:>2} {b['title'][:48]:48} | by {str(b['author'])[:28]}")
    if not unmatched:
        print("   (none)")

    print()
    print("-- REVIEW rows with no booklist counterpart --")
    used = {id(b["review"]) for b in book if b["review"]}
    orphans = [r for r in review if id(r) not in used]
    for r in orphans:
        print(f"   G{r['grade']:>2} {r['title'][:44]:44} | {r['category']}")
    if not orphans:
        print("   (none)")

    # ---- integrity gate: fail loudly rather than emitting a quiet half-dataset
    problems = []
    if unmatched:
        problems.append(f"{len(unmatched)} booklist entries did not join a review row")
    for b in book:
        if not b["title"]:
            problems.append(f"empty title: {b['listed_as'][:60]!r}")
        if b["title"].startswith("http"):
            problems.append(f"URL parsed as title: {b['title'][:60]!r}")
        if b["author"] and len(b["author"]) > 60:
            problems.append(f"author field too long (bad split): {b['author'][:60]!r}")
        if b["url"] and b["url_kind"] == "amazon" and not b["asin"]:
            problems.append(f"amazon product link with no ASIN: {b['title'][:40]!r}")
    dupes = [k for k, n in Counter(
        (b["grade"], b["key"]) for b in book).items() if n > 1]
    for d in dupes:
        problems.append(f"duplicate survived dedupe: {d}")

    if collapsed:
        print()
        print(f"-- collapsed {len(collapsed)} duplicate listing(s) in the source docx --")
        for g, k in collapsed:
            print(f"   G{g:>2} {k}")

    print()
    if problems:
        print(f"!! GATE: {len(problems)} problem(s)")
        for p in problems[:25]:
            print(f"   - {p}")
        sys.exit(1)
    print("GATE: clean")


if __name__ == "__main__":
    main()
