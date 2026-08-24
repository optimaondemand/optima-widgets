"""
resolve_editions.py — Stage 2 of the Optima literature spine.

Turns each booklist link into real bibliographic data: exact edition title,
publisher, edition year, and crucially the TRANSLATOR / EDITOR, which is what
actually decides rights on a pre-modern work.

Source of truth is Open Library. Google Books is NOT used: it returns HTTP 429
(daily quota exhausted) on the shared anonymous quota, so depending on it would
make this stage fail intermittently for reasons unrelated to the data.

Resolution ladder, per record:
  1. ISBN-10-shaped ASIN from the URL          -> /isbn/{isbn}.json
  2. a.co shortener                            -> resolve redirect, then (1)
  3. Kindle ASIN (B...), search URL, or no URL -> Open Library title search

Everything is cached to data/ol_cache.json. Re-runs are free and the API is not
hammered. Delete the cache to force a refetch.

Nothing here decides rights. It records who made the edition; stage 3 judges.

CAUTION, learned by smoke test: Open Library's `first_publish_date` is edition
metadata, not the work's first publication. It returned "January 17, 2007" for
Dante, 1588 for Sophocles' Electra, and "January 1999" for the Odyssey. It is
carried through as `ol_first_publish_raw` and must NOT be used as the
publication date. Stage 3 uses a curated first-publication table instead.
"""
import json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CACHE_PATH = DATA / "ol_cache.json"

UA = "OptimaLiteratureLibrary/1.0 (curriculum rights audit; jdrexel@optimaed.com)"
DELAY = 0.34          # ~3 req/s, polite
TIMEOUT = 25

# Roles we care about, and the abbreviations Open Library actually uses in
# `contributions` ("Smith, John, tr.") and free-text `by_statement`.
ROLE_PATTERNS = [
    ("translator", re.compile(
        r'\b(translated(?:\s+from[^;.]{0,40})?\s+by|translator|translation by|'
        r',\s*tr\.|,\s*trans\.)\s*:?\s*', re.I)),
    ("editor", re.compile(
        r'\b(edited(?:\s+and\s+\w+)?\s+by|editor|,\s*ed\.)\s*:?\s*', re.I)),
    ("illustrator", re.compile(
        r'\b(illustrated by|illustrator|,\s*ill\.)\s*:?\s*', re.I)),
    ("introduction", re.compile(
        r'\b(with an introduction by|introduction by|foreword by|'
        r'afterword by|notes by)\s*:?\s*', re.I)),
    ("reteller", re.compile(
        r'\b(retold by|adapted by|abridged by)\s*:?\s*', re.I)),
]

NAME_STOP = re.compile(
    r'\s*(?:;|\.\s*$|,\s*(?:with|and\s+(?:an?\s+)?(?:introduction|notes|preface))\b)')

# Open Library's OTHER contributions format puts the role in parentheses after
# the name: "Robert Fitzgerald (Translator)". Missing this silently dropped the
# Fitzgerald Odyssey translator, which is the single most consequential field
# in this whole dataset.
PAREN_ROLE = re.compile(r'^\s*(.+?)\s*\(\s*([A-Za-z][A-Za-z /.-]{2,30}?)\s*\)\s*$')

PAREN_ROLE_MAP = {
    "translator": "translator", "trans": "translator",
    "translated by": "translator",
    "editor": "editor", "ed": "editor", "edited by": "editor",
    "illustrator": "illustrator", "ill": "illustrator",
    "introduction": "introduction", "foreword": "introduction",
    "afterword": "introduction", "preface": "introduction",
    "notes": "introduction", "commentary": "introduction",
    "reteller": "reteller", "adapter": "reteller", "abridger": "reteller",
}


def load_cache():
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text(encoding="utf8"))
        except Exception:
            print("!! cache unreadable, starting fresh", file=sys.stderr)
    return {}


def save_cache(c):
    CACHE_PATH.write_text(json.dumps(c, indent=0, ensure_ascii=False), encoding="utf8")


RETRIES = 3


def get_json(url, cache, tag):
    """
    Cached GET with retry. Retries matter: a single connection timeout otherwise
    records a permanent 'unresolved' for a title that is perfectly resolvable,
    and an error is NOT cached so a later run can still succeed.
    """
    ck = f"{tag}::{url}"
    if ck in cache:
        return cache[ck]
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept": "application/json"})
    last = None
    for attempt in range(RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                val = json.loads(r.read().decode("utf8", "replace"))
            cache[ck] = val
            time.sleep(DELAY)
            return val
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
            time.sleep(DELAY * (attempt + 2) * 3)   # back off
    # deliberately NOT cached
    return {"__error__": last}


def resolve_short(url, cache):
    """a.co/d/XXXX -> final Amazon URL, so the ASIN can be read off it."""
    ck = f"short::{url}"
    if ck in cache:
        return cache[ck]
    final = None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            final = r.geturl()
    except Exception as e:
        try:
            # Some shorteners refuse HEAD-ish requests but answer a range GET.
            req = urllib.request.Request(
                url, headers={"User-Agent": UA, "Range": "bytes=0-2048"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                final = r.geturl()
        except Exception:
            final = f"__error__:{type(e).__name__}"
    cache[ck] = final
    time.sleep(DELAY)
    return final


ASIN_RE = [re.compile(p) for p in (
    r'/dp/([A-Z0-9]{10})(?:[/?]|$)',
    r'/ASIN/([A-Z0-9]{10})(?:[/?]|$)',
    r'/gp/product/([A-Z0-9]{10})(?:[/?]|$)',
)]


def asin_of(url):
    if not url or url.startswith("__error__"):
        return None
    for p in ASIN_RE:
        m = p.search(url)
        if m:
            return m.group(1)
    return None


def is_isbn10(s):
    return bool(s and re.match(r'^\d{9}[\dX]$', s))


def parse_roles(*texts):
    """
    Pull role -> name out of by_statement / contributions strings.
    Conservative on purpose: a name is only recorded when the role word is
    present. A guessed translator is worse than a blank field, because the whole
    point of this column is that someone can act on it.
    """
    found = {}
    for t in texts:
        if not t:
            continue
        if isinstance(t, list):
            for item in t:
                for k, v in parse_roles(item).items():
                    found.setdefault(k, v)
            continue
        s = str(t)

        # "Robert Fitzgerald (Translator)"
        pm = PAREN_ROLE.match(s)
        if pm:
            name, raw_role = pm.group(1).strip(" ,."), pm.group(2).strip().lower()
            role = PAREN_ROLE_MAP.get(raw_role.rstrip("."))
            if role and 2 < len(name) < 70 and role not in found:
                found[role] = re.sub(r'\s+', " ", name)
                continue

        for role, pat in ROLE_PATTERNS:
            if role in found:
                continue
            m = pat.search(s)
            if not m:
                continue
            tail = s[m.end():]
            # "Smith, John, tr." puts the name BEFORE the marker
            if m.group(1).strip().startswith(","):
                head = s[:m.start()].strip()
                name = head.split(";")[-1].strip(" ,.")
            else:
                name = NAME_STOP.split(tail)[0].strip(" ,.")
                name = re.split(r'\s+(?:and|with)\s+(?:an?\s+)?(?:introduction|notes|preface|foreword)\b',
                                name, flags=re.I)[0].strip(" ,.")
            name = re.sub(r'\s+', " ", name)
            if 2 < len(name) < 70:
                found[role] = name
    return found


def ol_by_isbn(isbn, cache):
    ed = get_json(f"https://openlibrary.org/isbn/{isbn}.json", cache, "isbn")
    if "__error__" in ed:
        return {"ok": False, "error": ed["__error__"], "isbn": isbn}
    out = {
        "ok": True,
        "isbn": isbn,
        "ol_edition": ed.get("key"),
        "edition_title": ed.get("title"),
        "subtitle": ed.get("subtitle"),
        "publishers": ed.get("publishers"),
        "publish_date": ed.get("publish_date"),
        "pages": ed.get("number_of_pages"),
        "by_statement": ed.get("by_statement"),
        "contributions": ed.get("contributions"),
        "series": ed.get("series"),
    }
    out["roles"] = parse_roles(ed.get("by_statement"), ed.get("contributions"))
    works = ed.get("works") or []
    if works:
        wk = works[0].get("key")
        if wk:
            w = get_json(f"https://openlibrary.org{wk}.json", cache, "work")
            if "__error__" not in w:
                out["ol_work"] = wk
                out["work_title"] = w.get("title")
                out["ol_first_publish_raw"] = w.get("first_publish_date")  # UNRELIABLE, see header
    return out


def ol_by_title(title, author, cache):
    q = {"title": title, "limit": "5",
         "fields": "key,title,author_name,first_publish_year,edition_count"}
    if author:
        q["author"] = author
    url = "https://openlibrary.org/search.json?" + urllib.parse.urlencode(q)
    js = get_json(url, cache, "search")
    if "__error__" in js:
        return {"ok": False, "error": js["__error__"]}
    docs = js.get("docs") or []
    if not docs:
        return {"ok": False, "error": "no search result"}
    d = docs[0]
    return {
        "ok": True,
        "via": "title-search",
        "ol_work": d.get("key"),
        "work_title": d.get("title"),
        "search_authors": d.get("author_name"),
        "ol_first_publish_raw": (str(d["first_publish_year"])
                                 if d.get("first_publish_year") else None),
        "edition_count": d.get("edition_count"),
        "roles": {},
    }


def main():
    recs = json.loads((DATA / "stage1_records.json").read_text(encoding="utf8"))
    book = recs["booklist"]
    cache = load_cache()

    stats = {"isbn": 0, "short_resolved": 0, "short_failed": 0,
             "title": 0, "failed": 0}
    try:
        for i, b in enumerate(book, 1):
            asin = b.get("asin")
            url = b.get("url")

            if not asin and b.get("url_kind") == "amazon_short" and url:
                final = resolve_short(url, cache)
                b["resolved_url"] = final
                asin = asin_of(final)
                if asin:
                    b["asin"] = asin
                    stats["short_resolved"] += 1
                else:
                    stats["short_failed"] += 1

            res = None
            if is_isbn10(asin):
                res = ol_by_isbn(asin, cache)
                if res.get("ok"):
                    stats["isbn"] += 1
            if not res or not res.get("ok"):
                r2 = ol_by_title(b["title"], b.get("author"), cache)
                if r2.get("ok"):
                    if res and not res.get("ok"):
                        r2["isbn_lookup_error"] = res.get("error")
                    res = r2
                    stats["title"] += 1
                else:
                    res = res or r2
                    stats["failed"] += 1
            b["edition"] = res

            if i % 25 == 0:
                save_cache(cache)
                print(f"  ...{i}/{len(book)}", flush=True)
    finally:
        save_cache(cache)

    (DATA / "stage2_records.json").write_text(
        json.dumps({"booklist": book, "review": recs["review"]},
                   indent=1, ensure_ascii=False), encoding="utf8")

    # ------------------------------------------------------------- report
    print()
    print(f"records            : {len(book)}")
    print(f"resolved by ISBN   : {stats['isbn']}")
    print(f"a.co resolved      : {stats['short_resolved']}"
          f"  (failed {stats['short_failed']})")
    print(f"resolved by title  : {stats['title']}")
    print(f"unresolved         : {stats['failed']}")
    print()

    roles_found = [b for b in book if (b.get("edition") or {}).get("roles")]
    print(f"records with a named role (translator/editor/etc): {len(roles_found)}")
    print()
    print("-- TRANSLATORS found (the column that decides rights) --")
    n = 0
    for b in book:
        r = (b.get("edition") or {}).get("roles") or {}
        if "translator" in r:
            n += 1
            print(f"   G{b['grade']:>2} {b['title'][:38]:38} | {r['translator'][:44]}")
    print(f"   ({n} total)")
    print()
    print("-- unresolved records --")
    for b in book:
        e = b.get("edition") or {}
        if not e.get("ok"):
            print(f"   G{b['grade']:>2} {b['title'][:40]:40} | {str(e.get('error'))[:44]}")


if __name__ == "__main__":
    main()
