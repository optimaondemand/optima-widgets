# -*- coding: utf-8 -*-
"""
build_reference_library.py — the ELA Reference Library (TEACHER facing).

Generates ela-reference-library.html: one page where a teacher can tell, at a
glance, which titles are free and which their students must buy, then build a
purchase list.

Sibling of the student Independent Reading library: same card anatomy
(.book/.bt/.ba/.bm, data-k search keys), same sans-serif rule. As of 2026-08-24
this page carries the new house style — official Optima brand tokens and Wix
Madefor type (see reference_library_assets.py); the student library is to be
restyled to match it, so the two read as one system again.

NEVER hand-edit the generated HTML. Change this file and re-run.

Signposting is one word, by design:
    FREE      public domain, and the free text IS the assigned text
    SIMILAR   free version exists but in a different translation/edition
    BUY       in copyright; students must obtain a licensed copy

Secondary badges: ARCHAIC (pre-1850 translation), OLDER (1850-99 translation),
VERIFY (a date or rights claim a human should confirm).

Degrades without JavaScript: every card is in the HTML, and the filter bar is
.js-only, hidden until the script runs. A Canvas iframe with a JS problem shows
the full list rather than a blank page.
"""
import html
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import course_editions as CE
import clt_titles as CT
import first_pub as FP
import genres as G

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "ela-reference-library.html"

import brand_assets as BRAND

# Superseded 2026-08-27 by the embedded wordmark in brand_assets.py, which
# already contains this owl. Kept in case the owl-only mark is wanted again.
OWL = ("https://raw.githubusercontent.com/optimaondemand/optima-assets/"
       "main/optima-owl.png")

# Optima brand guidelines v2.0 (July 2026). Binary Blue anchors the chrome,
# Bitstream Blue is the accent, and badges use the guide's darkened variants
# so white-on-colour text clears the 4.5:1 contrast rule.
NAVY, ACCENT = "#0E1C42", "#55C8E8"
TAUGHT_C = "#B85F00"   # Dark Odyssey Orange
CLT_C    = "#0E1C42"   # Binary Blue -- provenance, not a rights status

STATE_LABEL = {"identical": "Free", "similar": "Similar", "none": "Buy"}
STATE_COLOR = {"identical": "#4B7F20",   # Dark Gamer Green
               "similar": "#0E5568",     # Dark Bitstream Blue
               "none": "#B85F00"}        # Dark Odyssey Orange
STATE_BLURB = {
    "identical": "Public domain. The free text is the same text.",
    "similar":   "Free version available in a different translation or edition.",
    "none":      "In copyright. Students need a licensed copy.",
}

# One translation flag, not two. The 1850-1899 tier was retired 2026-08-27:
# it fired on a single title and told a teacher nothing they could act on.
# NOTE the key is "archaic" and the label is "Older". The key names the date
# rule in first_pub.flag_tier (pre-1850); the label is what a reader sees.
FLAG_LABEL = {"archaic": "Older"}
FLAG_COLOR = {"archaic": "#8F347F"}   # Dark Portal Purple
FLAG_TITLE = {
    "archaic": "Translation published before 1850",
}


def esc(s):
    return html.escape("" if s is None else str(s), quote=False)


def attr(s):
    return html.escape("" if s is None else str(s), quote=True)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")


def norm(s):
    return re.sub(r"[^a-z0-9 ]+", "", str(s).lower())


def year_label(work):
    """Human date from the curated table. Negative years are BC."""
    if not work:
        return None
    y, circa, _lang, _conf, _note = work
    if y is None:
        return None
    s = f"{abs(y)} BC" if y < 0 else str(y)
    return ("c. " + s) if circa else s


def sort_key(rec):
    """Alphabetical by title, articles ignored, the way a library shelves."""
    t = re.sub(r'^(the|a|an)\s+', "", rec["title"].lower()).strip()
    return (t, rec["title"].lower())


def author_sort(rec):
    a = rec.get("author") or ""
    toks = [w for w in re.sub(r'[^A-Za-z .\-]', " ", a).split() if len(w) > 1]
    return (toks[-1].lower() if toks else "zzz", rec["title"].lower())


# --------------------------------------------------------------- enrichment

def enrich(book):
    """Attach everything the page needs; leave gaps visible, never guessed."""
    for b in book:
        key = b["key"]
        work = FP.WORKS.get(key)
        b["_work"] = work
        b["_year"] = year_label(work)
        b["_year_num"] = work[0] if work else None
        b["_lang"] = work[2] if work else None
        b["_date_conf"] = work[3] if work else None
        b["_date_note"] = work[4] if work else None

        shelf, shelf_src = G.genre_for(b["title"], b.get("author"),
                                       b.get("kind"), b.get("grade"))
        b["_shelf"], b["_shelf_src"] = shelf, shelf_src

        fv = b.get("free_version") or {"state": "none", "reason": "unknown_rights"}
        b["_state"] = fv["state"]
        b["_reason"] = fv.get("reason")

        # Buy-side edition detail, from the ISBN resolution pass.
        ed = b.get("edition") or {}
        roles = ed.get("roles") or {}
        b["_translator"] = roles.get("translator")
        b["_editor"] = roles.get("editor")
        b["_illustrator"] = roles.get("illustrator")
        b["_reteller"] = roles.get("reteller")
        b["_publisher"] = (ed.get("publishers") or [None])[0]
        b["_edition_year"] = ed.get("publish_date")
        b["_pages"] = ed.get("pages")
        b["_isbn"] = ed.get("isbn") or b.get("asin")
        b["_edition_title"] = ed.get("edition_title") or ed.get("work_title")

        # If no translator was resolved from the ISBN, fall back to the one the
        # book list states in prose ("translated by Robert Fitzgerald").
        if not b["_translator"] and b.get("edition_hint"):
            m = re.search(r'translat\w*\s*(?:by)?\s*(.+)$', b["edition_hint"], re.I)
            if m:
                b["_translator"] = m.group(1).strip(" .,")

        # Archaic / older flag keys off the TRANSLATION's year, never the work's.
        #
        # It must consider the TAUGHT edition as well as the purchasable one.
        # The pre-1850 case in this corpus (Chase's Aristotle, 1847) and both
        # 1850-99 cases (Long's Meditations, Arnold's Gita) are all editions
        # Optima teaches, and the book list names no translator for any of them
        # -- so a buy-side-only flag rendered on zero cards.
        taught = CE.COURSE.get(key) or {}

        def year_of(text):
            """Match any known translator surname inside a free-text edition."""
            if not text:
                return None, None
            words = {w.lower() for w in re.findall(r'[A-Za-z]{3,}', text)}
            for surname, info in FP.TRANSLATIONS.items():
                if surname in words:
                    return info["year"], info["name"]
            return None, None

        buy_year, _ = year_of(b["_translator"])
        taught_year, taught_name = year_of(taught.get("edition"))

        # Prefer the taught edition: it is the authoritative one, and it is what
        # a student in an Optima course will actually be reading.
        if taught_year is not None:
            tyear, tsource, tname = taught_year, "taught", taught_name
        elif buy_year is not None:
            tyear, tsource, tname = buy_year, "listed", b["_translator"]
        else:
            tyear, tsource, tname = None, None, None

        b["_translation_year"] = tyear
        b["_flag_source"] = tsource
        b["_flag_translator"] = tname
        b["_flag"] = FP.flag_tier(tyear, b["_lang"]) if tyear is not None else "none"
        if b["_flag"] == "unknown":
            b["_flag"] = "none"          # unknown translation year is not a warning
        if b["_flag"] == "older":
            b["_flag"] = "none"          # retired tier: 1850-1899 no longer flagged

        # What the built coursework actually teaches. This is the authoritative
        # layer: the other two lists are organised by title, and rights live in
        # the edition.
        c = CE.COURSE.get(key)
        b["_course"] = c
        # Every title in this catalogue is parsed from the official book list,
        # so book-list membership is universal here. Kept as a field rather
        # than hardcoded at the badge, so the day the catalogue takes in a
        # title from somewhere else this is the one line that has to change.
        b["_taught"] = True
        b["_clt"] = CT.is_clt(b["grade"], b["title"])
        b["_clt_bank"] = CT.bank_entry(b["grade"], b["title"])
        b["_course_verify"] = bool(c and c.get("verify"))

        b["_verify"] = (b["_date_conf"] == "verify") or b["_course_verify"]
    return book



# ------------------------------------------------------- teacher bookshelves

CLASSROOMS = ROOT / "classrooms.json"


def load_classrooms():
    """The shelves teachers have published, from the file the team maintains.

    Missing file is not an error: a school year starts with nobody's shelf in
    yet, and the Teacher Bookshelves view says so rather than looking broken.
    A malformed file IS an error, because a silently-empty directory would read
    as "no teacher has chosen anything" when the truth is "the file is wrong".
    """
    if not CLASSROOMS.exists():
        return "", []
    raw = json.loads(CLASSROOMS.read_text(encoding="utf8"))
    if not isinstance(raw, dict):
        raise SystemExit("classrooms.json: top level must be an object")
    year = raw.get("school_year") or ""
    rooms = raw.get("classrooms")
    if rooms is None:
        raise SystemExit('classrooms.json: no "classrooms" key')
    if not isinstance(rooms, list):
        raise SystemExit('classrooms.json: "classrooms" must be a list')
    out = []
    for i, c in enumerate(rooms):
        where = f"classrooms[{i}]"
        for req in ("teacher", "course", "grade", "titles"):
            if not c.get(req):
                raise SystemExit(f"{where}: missing required field {req!r}")
        if not isinstance(c["titles"], list):
            raise SystemExit(f"{where}: titles must be a list")
        delivery = c.get("delivery") or "Live"
        if delivery not in ("Live", "On-Demand"):
            raise SystemExit(f"{where}: delivery must be Live or On-Demand, "
                             f"got {delivery!r}")
        level = c.get("level") or ""
        if level not in ("", "Honors", "AP"):
            raise SystemExit(f"{where}: level must be blank, Honors or AP, "
                             f"got {level!r}")
        out.append({
            "teacher": c["teacher"], "course": c["course"],
            "subject": c.get("subject") or "ELA", "grade": str(c["grade"]),
            "level": level, "delivery": delivery,
            "period": c.get("period") or None,
            "titles": list(c["titles"]),
        })
    return year, out


# ------------------------------------------------------------------ rendering

# A link labelled "Read free" next to a pill reading FREE says the same thing
# twice. Naming the SOURCE removes the redundancy and tells the teacher
# something they did not already know.
SOURCE_NAME = {
    "gutenberg": "Project Gutenberg",
    "gutenberg.org": "Project Gutenberg",
    "gutenberg.net.au": "Gutenberg Australia",
    "gutenberg.ca": "Gutenberg Canada",
    "en.wikisource.org": "Wikisource",
    "wikisource.org": "Wikisource",
    "standardebooks.org": "Standard Ebooks",
    "guides.loc.gov": "Library of Congress",
    "loc.gov": "Library of Congress",
    "folger.edu": "Folger",
    "folger-main-site-assets.s3.amazonaws.com": "Folger",
    "americanenglish.state.gov": "American English (US State Dept)",
    "fordlibrarymuseum.gov": "Ford Presidential Library",
    "americanliterature.com": "American Literature",
    "archive.org": "Internet Archive",
    "poetryfoundation.org": "Poetry Foundation",
    "poetryverse.com": "PoetryVerse",
    "poets.org": "Poets.org",
}

VENDOR_NAME = {
    "amazon.com": "Amazon", "www.amazon.com": "Amazon", "a.co": "Amazon",
    "folger.edu": "Folger", "guides.loc.gov": "Library of Congress",
}


def _host(url):
    m = re.match(r'https?://([^/]+)', url or "")
    return (m.group(1).lower() if m else "")


def source_label(host_or_name):
    h = (host_or_name or "").lower().replace("www.", "")
    return SOURCE_NAME.get(h, host_or_name or "source")


def vendor_label(url):
    h = _host(url).replace("www.", "")
    return VENDOR_NAME.get(h, h or "purchase")


def action_links(b):
    fv = b.get("free_version") or {}
    free = fv.get("free") or {}
    ro = fv.get("read_online") or {}
    out = []
    if b.get("url"):
        out.append(f'<a class="act buy" href="{attr(b["url"])}" target="_blank" '
                   f'rel="noopener" title="Buy the edition the book list names">'
                   f'{esc(vendor_label(b["url"]))}</a>')
    if free.get("url"):
        cls = "free" if b["_state"] == "identical" else "sim"
        tip = ("The public-domain text, same as the assigned text"
               if b["_state"] == "identical"
               else "A different translation or edition from the one listed")
        out.append(f'<a class="act {cls}" href="{attr(free["url"])}" '
                   f'target="_blank" rel="noopener" title="{attr(tip)}">'
                   f'{esc(source_label(free.get("source")))}</a>')
    if ro.get("url"):
        out.append(f'<a class="act ro" href="{attr(ro["url"])}" target="_blank" '
                   f'rel="noopener" title="Read on the publisher\'s site; '
                   f'not a download">{esc(source_label(ro.get("source")))}</a>')
    return "".join(out)


def pub_line(b):
    """The specific-information line: who made THIS edition."""
    bits = []
    if b["_translator"]:
        bits.append(f'trans. {esc(b["_translator"])}')
    if b["_editor"]:
        bits.append(f'ed. {esc(b["_editor"])}')
    if b["_reteller"]:
        bits.append(f'retold by {esc(b["_reteller"])}')
    if b["_illustrator"]:
        bits.append(f'illus. {esc(b["_illustrator"])}')
    if b["_publisher"]:
        bits.append(esc(b["_publisher"]))
    if b["_edition_year"]:
        bits.append(esc(b["_edition_year"]))
    if b["_isbn"]:
        bits.append(f'ISBN {esc(b["_isbn"])}')
    return " &middot; ".join(bits)


def course_line(b):
    """
    What the built coursework uses. Only rendered for taught titles, because
    for everything else there is nothing true to say.
    """
    c = b.get("_course")
    if not c:
        return ""
    if c["used"] == "student":
        body = ("Taught in Optima Grade %s. Students supply their own copy; "
                "no text is reproduced." % esc(c["grade"]))
    elif c["used"] == "reference":
        body = ("In the Grade %s folder as a reading copy only, not deployed."
                % esc(c["grade"]))
    else:
        ed = c.get("edition")
        body = "Optima Grade %s uses %s." % (
            esc(c["grade"]), esc(ed) if ed else "an unattributed edition")
    warn = ""
    if c["used"] == "on-page" and c.get("stored_ok") is False:
        warn = ' <b style="color:#B85F00;">File needs attention.</b>'
    return f'<div class="course">{body}{warn}</div>'


def book_card(b, idx):
    badges = [f'<span class="bdg st" style="--bc:{STATE_COLOR[b["_state"]]};" '
              f'title="{attr(STATE_BLURB[b["_state"]])}">'
              f'{STATE_LABEL[b["_state"]]}</span>']
    if b["_flag"] in FLAG_LABEL:
        who = b.get("_flag_translator")
        yr = b.get("_translation_year")
        which = ("the edition Optima teaches" if b.get("_flag_source") == "taught"
                 else "the edition the book list names")
        tip = FLAG_TITLE[b["_flag"]]
        if who and yr:
            tip = f"{tip}. {who}, {yr} — {which}."
        badges.append(f'<span class="bdg" style="--bc:{FLAG_COLOR[b["_flag"]]};" '
                      f'title="{attr(tip)}">{FLAG_LABEL[b["_flag"]]}</span>')
    if b["_verify"]:
        badges.append(f'<span class="bdg" style="--bc:#67308F;" '
                      f'title="{attr(b["_date_note"] or "Needs a human check")}">'
                      f'Verify</span>')
    if b["_reason"] == "needs_sourcing":
        badges.append('<span class="bdg" style="--bc:#51617C;" '
                      'title="Public domain, but no trusted free source found yet">'
                      'No source</span>')

    if b.get("_clt"):
        bank = b.get("_clt_bank") or ""
        badges.insert(0, f'<span class="bdg" style="--bc:{CLT_C};" '
                         f'title="{attr("In the CLT Author Bank: " + bank)}">'
                         f'CLT</span>')

    if b["_taught"]:
        c = b["_course"]
        tip = ("On the OAO 2026-27 approved book list")
        if c:
            tip += ". " + {
                "on-page": "Optima reproduces this text in the coursework",
                "student": "Students supply their own copy",
                "reference": "In the course folder as a reading copy only",
            }[c["used"]]
        badges.insert(0, f'<span class="bdg tg" style="--bc:{TAUGHT_C};" '
                         f'title="{attr(tip)}">&#9733; Taught</span>')

    art, colour = G.SHELF_ART.get(b["_shelf"], G.SHELF_ART["Unclassified"])
    # An em dash must be a real character here, not an entity: esc() escapes the
    # ampersand and the card would show the literal text "&mdash;".
    who = b.get("author") or (", ".join(b["authors"]) if b.get("authors") else "—")
    yr = f'<span class="yr">{esc(b["_year"])}</span>' if b["_year"] else ""
    pl = pub_line(b)

    # Cover art from Open Library's ISBN cover service (the same source the
    # edition data already comes from). ?default=false makes a miss a 404, the
    # onerror hides the img, and the genre-coloured spine placeholder beneath
    # shows through — so titles with no ISBN, and ASINs Open Library does not
    # know, degrade to a spine rather than a broken image.
    cover = f'<div class="cover-ph"><span>{esc(b["title"])}</span></div>'
    if b["_isbn"]:
        cover += (f'<img class="cover" loading="lazy" alt="" '
                  f'src="https://covers.openlibrary.org/b/isbn/'
                  f'{attr(str(b["_isbn"]).strip())}-M.jpg?default=false" '
                  f'onerror="this.style.display=\'none\'" />')

    return (
        f'<div class="book" style="--sc:{colour};" data-i="{idx}" '
        f'data-k="{attr(norm(b["title"]) + " " + norm(who) + " " + norm(b["_shelf"]))}" '
        f'data-grade="{attr(b["grade"])}" data-shelf="{attr(slug(b["_shelf"]))}" '
        f'data-state="{attr(b["_state"])}" data-author="{attr(author_sort(b)[0])}">'
        f'<label class="pick"><input type="checkbox" class="cb" '
        f'data-i="{idx}" aria-label="Add {attr(b["title"])} to my list"><span></span></label>'
        f'<div class="brow">'
        f'<div class="cwrap">{cover}</div>'
        f'<div class="bhead">'
        f'<div class="bt">{esc(b["title"])}</div>'
        f'<div class="ba">{esc(who) if not b.get("authors") else who}{yr}</div>'
        f'<div class="shelf">{art} {esc(b["_shelf"])}'
        f'<span class="gr">Gr {esc(b["grade"])}</span></div>'
        f'</div></div>'
        + (f'<div class="pub">{pl}</div>' if pl else "")
        + course_line(b)
        + f'<div class="bm">{"".join(badges)}</div>'
        f'<div class="acts">{action_links(b)}</div>'
        '</div>'
    )


# ------------------------------------------------------- client-side records

def client_record(b, idx):
    """Compact mirror of each card for the filter/sort/list JS."""
    fv = b.get("free_version") or {}
    free = fv.get("free") or {}
    who = b.get("author") or (", ".join(b["authors"]) if b.get("authors") else "")
    g = b["grade"]
    return {
        "id": f'{g}-{slug(b["title"])[:44]}',
        "i": idx,
        "title": b["title"],
        "authorDisplay": who,
        "authorKey": author_sort(b)[0],
        "grade": g,
        "gradeNum": 0 if g == "K" else int(g),
        "shelf": b["_shelf"],
        "shelfSlug": slug(b["_shelf"]),
        "state": b["_state"],
        "taught": "yes" if b["_taught"] else "no",
        "clt": "yes" if b.get("_clt") else "no",
        "cltBank": b.get("_clt_bank"),
        "courseNote": (b["_course"] or {}).get("note"),
        "courseEdition": (b["_course"] or {}).get("edition"),
        "courseUse": (b["_course"] or {}).get("used"),
        "year": b["_year"],
        "translator": b["_translator"],
        "editor": b["_editor"],
        "publisher": b["_publisher"],
        "editionYear": b["_edition_year"],
        "isbn": b["_isbn"],
        "buyUrl": b.get("url"),
        "freeUrl": free.get("url"),
        "sortTitle": sort_key(b)[0],
        "k": norm(b["title"] + " " + who + " " + b["_shelf"]),

        # --- extra fields the comparison views need
        "listedEdition": b.get("edition_hint"),
        "freeSource": free.get("source"),
        "freeReason": fv.get("reason"),
        "freeMatchedTitle": free.get("matched_title"),
        "readOnlineUrl": (fv.get("read_online") or {}).get("url"),
        "flag": b["_flag"],
        "flagTranslator": b.get("_flag_translator"),
        "flagYear": b.get("_translation_year"),
        "flagSource": b.get("_flag_source"),
        "verify": bool(b["_verify"]),
        "verifyNote": b.get("_date_note") or (b.get("_course") or {}).get("note"),
        "reviewCategory": (b.get("review") or {}).get("category"),
        "taughtEdition": (b.get("_course") or {}).get("edition"),
        "taughtUse": (b.get("_course") or {}).get("used"),
        "taughtGrade": (b.get("_course") or {}).get("grade"),
        "storedFileOk": (b.get("_course") or {}).get("stored_ok"),
        "firstPub": b["_year"],
        "dateConfidence": b["_date_conf"],
    }


# ------------------------------------------------------------------- the page

def key_block():
    items = []
    for st in ("identical", "similar", "none"):
        items.append(
            f'<div class="keyitem">'
            f'<span class="bdg" style="--bc:{STATE_COLOR[st]};">{STATE_LABEL[st]}</span>'
            f'{esc(STATE_BLURB[st])}</div>')
    for fl in ("archaic",):
        items.append(
            f'<div class="keyitem">'
            f'<span class="bdg" style="--bc:{FLAG_COLOR[fl]};">{FLAG_LABEL[fl]}</span>'
            f'{esc(FLAG_TITLE[fl])}</div>')
    items.append(
        '<div class="keyitem"><span class="bdg" style="--bc:#67308F;">Verify</span>'
        'A date or rights claim that still needs a human check</div>')
    items.insert(0,
        f'<div class="keyitem">'
        f'<span class="bdg" style="--bc:{CLT_C};">CLT</span>'
        f'By an author in the Classic Learning Test Author Bank. CLT publishes '
        f'authors, not titles, so this marks the author, not the exact book</div>')
    items.insert(0,
        f'<div class="keyitem">'
        f'<span class="bdg tg" style="--bc:{TAUGHT_C};">&#9733; Taught</span>'
        f'On the OAO 2026-27 approved book list. Every title here carries it. '
        f'Where a course has an audited edition, the gold note on the card names '
        f'it, and that edition is what settles rights</div>')
    return (
        '<div class="key"><h2>What the words mean</h2>'
        f'<div class="keyrow">{"".join(items)}</div>'
        '<p class="fine">A free PDF on a school or personal website is not a '
        'licence. Free versions here come only from Project Gutenberg, Standard '
        'Ebooks, Wikisource, the Library of Congress, the Folger, and government '
        'archives. Where a work is public domain but no trusted source has been '
        'found, the card says <b>No source</b> rather than guessing.</p>'
        '<p class="fine">Titles marked <b>Similar</b> are a different translation '
        'or edition from the one the book list specifies. They are fine for '
        'reference and for a student who cannot buy the book, but do not assign '
        'by page or line number across two different versions.</p>'
        '</div>')


def controls(book):
    grades = sorted({b["grade"] for b in book},
                    key=lambda g: 0 if g == "K" else int(g))
    shelves = sorted({b["_shelf"] for b in book})

    gopt = "".join(f'<option value="{attr(g)}">Grade {esc(g)}</option>'
                   for g in grades)
    sopt = "".join(f'<option value="{attr(slug(s))}">{esc(s)}</option>'
                   for s in shelves)
    stopt = "".join(f'<option value="{attr(s)}">{esc(STATE_LABEL[s])}</option>'
                    for s in ("identical", "similar", "none"))
    # Was a Taught filter. Every title on this page is now Taught, so that
    # control could only return all 226 or none. CLT membership is the thing
    # that actually divides the list, so the slot goes to it.
    topt = ('<option value="">Every title</option>'
            '<option value="yes">In the CLT Author Bank</option>'
            '<option value="no">Not in the CLT bank</option>')

    sorts = [("az", "A&ndash;Z"), ("author", "By author"),
             ("grade", "By grade"), ("shelf", "By genre")]
    sbtn = "".join(
        f'<button class="tab sortbtn" data-sort="{s}" '
        f'aria-pressed="{"true" if s == "az" else "false"}">{lbl}</button>'
        for s, lbl in sorts)

    # Named views. Each answers a question a teacher actually arrives with,
    # rather than making them assemble it out of filters. The two data-audit
    # views stay fully functional but live behind the gear, so a teacher sees
    # three tabs and the rights bookkeeping stays out of their way
    # (Jessica's feedback, 2026-08-21; scoped with Jorge, 2026-08-24).
    views = [
        ("library",  "&#128218;", "All titles",
         "Every title as a card"),
        ("compare",  "&#8646;",   "Buy vs free",
         "Side by side, where both exist"),
        ("grades",   "&#128202;", "Cost by grade",
         "What each grade must purchase"),
        ("mine",     "&#9998;",   "My Classroom",
         "Choose the titles you are teaching this year"),
        ("shelves",  "&#128214;", "Teacher Bookshelves",
         "What every teacher has selected from the approved list"),
    ]
    admin_views = [
        ("sources",  "&#128209;", "Three lists",
         "Book list vs review sheet vs what is taught"),
        ("attention", "&#9888;",  "Needs attention",
         "Unverified claims and broken files"),
    ]
    vbtn = "".join(
        f'<button class="vtab" data-view="{v}" '
        f'aria-pressed="{"true" if v == "library" else "false"}" '
        f'title="{attr(tip)}">{icon} {lbl}</button>'
        for v, icon, lbl, tip in views)
    abtn = "".join(
        f'<button class="vtab admin" data-view="{v}" aria-pressed="false" '
        f'title="{attr(tip)}">{icon} {lbl}</button>'
        for v, icon, lbl, tip in admin_views)

    return (
        '<div class="viewbar js-only" id="viewbar">'
        f'<div class="vrow">{vbtn}{abtn}'
        '<button class="gearbtn" id="adminToggle" aria-expanded="false" '
        'title="Data checks: rights bookkeeping and open questions">&#9881; '
        'Data checks</button>'
        '</div></div>'
        '<div class="controls js-only">'
        '<div class="crow">'
        '<span class="lbl">Find</span>'
        '<input id="q" type="search" placeholder="Search title, author, genre&hellip;" '
        'aria-label="Search the library">'
        f'<select id="fGrade" aria-label="Filter by grade"><option value="">All grades</option>{gopt}</select>'
        f'<select id="fShelf" aria-label="Filter by genre"><option value="">All genres</option>{sopt}</select>'
        f'<select id="fState" aria-label="Filter by access"><option value="">Free and paid</option>{stopt}</select>'
        f'<select id="fClt" aria-label="Filter by CLT Author Bank membership">{topt}</select>'
        '</div>'
        '<div class="crow">'
        '<span class="lbl">Shelve</span>'
        f'{sbtn}'
        '<span class="count" id="count"></span>'
        '</div>'
        '</div>')


def build():
    src = DATA / "stage3_records.json"
    if not src.exists():
        raise SystemExit("run match_free.py first (data/stage3_records.json missing)")
    recs = json.loads(src.read_text(encoding="utf8"))

    # Known typos in the source .docx, corrected before anything is derived
    # from the title: the id, the search key and the printed book list all
    # come off it.
    import source_corrections as SC
    fixed = SC.apply_to_records(recs["booklist"])
    for old, new in fixed:
        print("  source correction: %r -> %r" % (old, new))

    book = enrich(recs["booklist"])
    book.sort(key=sort_key)

    cards, client = [], []
    for i, b in enumerate(book):
        cards.append(book_card(b, i))
        client.append(client_record(b, i))

    # Teacher shelves name catalogue ids. An id that does not resolve would
    # render as a blank line on a shelf, so it fails the build instead.
    year, shelves = load_classrooms()
    known = {c["id"] for c in client}
    for room in shelves:
        for tid in room["titles"]:
            if tid not in known:
                raise SystemExit(
                    f'classrooms.json: {room["teacher"]} / {room["course"]} '
                    f'names unknown title id {tid!r}')

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>ELA Reference Library &middot; Optima Academy Online</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Wix+Madefor+Display:wght@600;700;800&amp;family=Wix+Madefor+Text:ital,wght@0,400;0,500;0,600;0,700;1,400&amp;display=swap" />
<style>{ASSETS.CSS}</style>
</head>
<body>
<div class="sheet">

<div class="hero">
  <div class="brandrow">
    <img class="oaologo" src="{BRAND.OAO_LOGO}"
      width="{BRAND.OAO_LOGO_W // 2}" height="{BRAND.OAO_LOGO_H // 2}"
      alt="Optima Academy Online" />
    <div>
      <h1>ELA <span class="accent">Reference Library</span></h1>
      <div class="sub">Every title on the Optima book list, K&ndash;12, with what
      it costs a family and what a teacher can hand out for free. Tick the box on
      any card to build a purchase list.</div>
    </div>
  </div>
</div>

{key_block()}
{controls(book)}

<div class="grid" id="grid">
{chr(10).join(cards)}
</div>

<!-- Alternate views render here. Empty and hidden until a view is chosen, so
     with JavaScript off the card grid above remains the whole page. -->
<div id="views" class="views" hidden></div>

<button class="fab" id="fab" style="display:none;">My list <b id="fabN">0</b></button>
<div class="panel" id="panel"><div class="sheetbox" id="listBox"></div></div>

</div>
<script>window.__LIB__ = {json.dumps(client, ensure_ascii=False)};
window.__SHELVES__ = {json.dumps(shelves, ensure_ascii=False)};
window.__SCHOOL_YEAR__ = {json.dumps(year)};</script>
<script>{JSMOD.JS}</script>
</body>
</html>
"""
    return page, book, client


# ------------------------------------------------------------------- the gate

# "sans-serif" CONTAINS "serif". A naive /serif/ guard fires on every correct
# stylesheet in the project, which is the harness being wrong rather than the
# page. Require a serif family that is not preceded by "sans-".
SERIF_RE = re.compile(r'font-family:[^;}]*?(?<!sans-)\b(serif|Georgia|'
                      r'"?Times New Roman"?|Garamond|Baskerville)\b', re.I)


def _self_test_guards():
    """A guard nobody tested is a guess. Assert both directions."""
    must_pass = [
        'font-family:"Segoe UI",Roboto,Helvetica,Arial,sans-serif;',
        "font-family:inherit;",
        'font-family: system-ui, -apple-system, sans-serif;',
    ]
    must_fail = [
        'font-family:Georgia,"Times New Roman",serif;',
        "font-family: serif;",
        'font-family:Garamond,serif;',
    ]
    bad = []
    for s in must_pass:
        if SERIF_RE.search(s):
            bad.append(f"SERIF_RE wrongly flagged: {s!r}")
    for s in must_fail:
        if not SERIF_RE.search(s):
            bad.append(f"SERIF_RE missed a real serif: {s!r}")
    if bad:
        for b in bad:
            print("  GUARD SELF-TEST FAIL:", b)
        raise SystemExit("gate guards are unsound; fix before trusting the gate")


def gate(page, book, client):
    _self_test_guards()
    problems, warn = [], []

    # structural markers the JS depends on
    for marker in ('id="grid"', 'id="q"', 'id="fGrade"', 'id="fShelf"',
                   'id="fState"', 'id="fab"', 'id="panel"',
                   'id="listBox"', 'id="count"', 'sortbtn', 'id="fClt"',
                   'id="views"', 'class="vtab"',
                   'id="viewbar"', 'id="adminToggle"', 'class="vtab admin"',
                   'data-view="compare"', 'data-view="grades"',
                   'data-view="sources"', 'data-view="attention"',
                   'data-view="mine"', 'data-view="shelves"',
                   'window.__SHELVES__', 'window.__SCHOOL_YEAR__',
                   'window.__LIB__',
                   'fonts.googleapis.com/css2?family=Wix+Madefor',
                   'covers.openlibrary.org', 'class="cover-ph"',
                   'class="oaologo"', 'data:image/png;base64,',
                   'cardhead', 'ch-stamp'):
        if marker not in page:
            problems.append(f"missing structural marker: {marker}")

    # removed on purpose (2026-08-24): stat counters, the author dropdown,
    # and the Translations view. If one reappears, someone merged old code.
    for gone in ('class="stat"', 'id="fAuthor"', 'data-view="editions"',
                 'class="spines"'):
        if gone in page:
            problems.append(f"removed element has reappeared: {gone}")

    # the .closest() bug that made the student menus inoperable. Scan only
    # non-comment script lines, so the comment explaining the bug cannot trip it.
    in_script, bad_closest = False, []
    for ln in page.splitlines():
        s = ln.strip()
        if s.startswith("<script"):
            in_script = True
            continue
        if s.startswith("</script"):
            in_script = False
            continue
        if not in_script:
            continue
        if s.startswith("//") or s.startswith("/*") or s.startswith("*"):
            continue
        if ".closest(" in s:
            bad_closest.append(s[:80])
    if bad_closest:
        problems.append(f".closest() in live script: {bad_closest[:2]}")

    # The .js-only reveal must REMOVE the class. Setting style.display = '' only
    # clears the inline style, so the stylesheet's .js-only{display:none} wins
    # and the entire toolbar stays invisible -- which is exactly what shipped
    # and made the page look like it had no controls at all.
    if ".js-only" in page:
        if "classList.remove('js-only')" not in page:
            problems.append(".js-only elements are never un-hidden by class removal")
        if re.search(r"js-only[^;]{0,400}?style\.display\s*=\s*['\"]{2}", page, re.S):
            problems.append("reveal uses style.display='' which cannot beat the "
                            "stylesheet rule; remove the class instead")

    # every card must be addressable and every client record must pair with one
    n_cards = page.count('class="book"')
    if n_cards != len(book):
        problems.append(f"{n_cards} cards rendered for {len(book)} records")
    if len(client) != len(book):
        problems.append(f"{len(client)} client records for {len(book)} cards")
    ids = [c["id"] for c in client]
    dupe = [k for k, n in Counter(ids).items() if n > 1]
    if dupe:
        problems.append(f"duplicate client ids: {dupe[:4]}")

    # the house rules
    if re.search(r'\bfacilitator\b', page, re.I):
        problems.append('says "facilitator"; house rule is "teacher"')
    if SERIF_RE.search(page):
        problems.append("serif font present; the library is sans-serif only")
    for day in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday"):
        if day in page:
            problems.append(f"weekday name in curriculum text: {day}")
    if "preview-banner" in page:
        problems.append("preview banner present")

    # rights safety: no free link may be offered on an in-copyright title
    for b in book:
        fv = b.get("free_version") or {}
        if (b.get("review") or {}).get("category") == "COPYRIGHT" and fv.get("free"):
            problems.append(f"free link on in-copyright title: {b['title']!r}")

    # flag correctness, both directions
    for b in book:
        if b["_flag"] in FLAG_LABEL and b["_lang"] in FP.ENGLISH_ORIGINAL:
            problems.append(f"translation flag on an English original: {b['title']!r}")
        if b["_flag"] == "older":
            problems.append(
                f"retired 'older' flag reappeared on {b['title']!r} - the "
                f"1850-1899 tier was removed 2026-08-27")
        if b["_flag"] == "archaic" and (b["_translation_year"] or 9999) >= 1850:
            problems.append(f"archaic flag on a post-1850 translation: {b['title']!r}")

    # warnings: real gaps, not defects
    unshelved = [b["title"] for b in book if b["_shelf"] == "Unclassified"]
    if unshelved:
        warn.append(f"{len(unshelved)} title(s) with no genre assigned: {unshelved[:5]}")
    nodate = [b["title"] for b in book if not b["_year"]]
    if nodate:
        warn.append(f"{len(nodate)} title(s) with no curated first-publication date")
    noed = [b["title"] for b in book if not b["_isbn"]]
    if noed:
        warn.append(f"{len(noed)} title(s) with no ISBN resolved")

    for w in warn:
        print(f"  warn: {w}")
    if problems:
        print(f"\n!! GATE: {len(problems)} problem(s)")
        for p in problems[:25]:
            print("   -", p)
        raise SystemExit(1)
    print("GATE: clean")


def main():
    global ASSETS
    import reference_library_assets as ASSETS_MOD
    import reference_library_js as JS_MOD
    ASSETS = ASSETS_MOD
    globals()["JSMOD"] = JS_MOD
    page, book, client = build()
    gate(page, book, client)
    OUT.write_text(page, encoding="utf8")
    kb = len(page.encode("utf8")) / 1024
    print(f"\nwrote {OUT.name}  ({kb:.0f} KB, {len(book)} cards)")
    st = Counter(b["_state"] for b in book)
    print(f"  free/same {st.get('identical',0)} | "
          f"free/similar {st.get('similar',0)} | buy {st.get('none',0)}")
    fl = Counter(b["_flag"] for b in book if b["_flag"] != "none")
    if fl:
        print("  translation flags:", dict(fl))


ASSETS = None
JSMOD = None

if __name__ == "__main__":
    main()
