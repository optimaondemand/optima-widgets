# -*- coding: utf-8 -*-
"""
course_editions.py — what the built coursework ACTUALLY uses.

The third authority, and the only one that settles the question teachers keep
asking. The official book list says what a family may buy. The copyright review
says what a title's status probably is. Neither records the EDITION a course
teaches, and rights live in the edition.

Source: audit of the course folders and generated GitHub lesson pages on
2026-08-20/21 -- the credit lines the lessons themselves carry, not inference.

Fields per entry:
  grade         Optima grade the coursework sits in
  used          "on-page"  text is reproduced in Optima coursework
                "student"  students obtain their own copy; Optima reproduces none
                "reference" present in the folder as a reading copy only
  edition       the translation/edition credited on the page, or None
  stored_ok     True  file in the folder is clean and usable
                False file has a problem (see note)
                None  not applicable / no stored file
  note          what a human needs to know
  verify        True when the coursework makes a rights claim that cannot be
                checked from the page itself. These are the actionable gaps.

Keys match parse_sources.joinkey(): normalised title + "|" + author surname.
"""

COURSE = {
    # ---------------------------------------------------------------- Grade 6
    "tales from shakespeare|lamb": dict(
        grade="6", used="on-page", edition="Charles & Mary Lamb, Project Gutenberg #573",
        stored_ok=True, verify=False,
        note="Print-to-PDF of PG #573; PDF metadata still names the Gutenberg source."),
    "golden touch|hawthorne": dict(
        grade="6", used="on-page", edition="Hawthorne, A Wonder-Book (1851)",
        stored_ok=True, verify=False, note="Clean Word-to-PDF with source line on p.1."),
    "adventures of robin hood|green": dict(
        grade="6", used="reference", edition="Roger Lancelyn Green, Puffin",
        stored_ok=False, verify=False,
        note="Full 263pp calibre-converted ebook in the folder. In copyright; "
             "never deployable."),
    "king arthur and his knights of the round table|green": dict(
        grade="6", used="reference", edition="Roger Lancelyn Green, Puffin 1953",
        stored_ok=False, verify=False,
        note="Full 275pp scan. Illustrations (c) 1953 Lotte Reiniger."),
    "bronze bow|speare": dict(
        grade="6", used="reference", edition="Houghton Mifflin",
        stored_ok=False, verify=False,
        note="Full 185pp calibre ebook; copyright page carries a Permissions notice."),
    "st george and the dragon|lotti": dict(
        grade="6", used="reference", edition="Michael Lotti, 2014",
        stored_ok=False, verify=False,
        note="Full 152pp calibre ebook. Self-published: permission means "
             "emailing the author."),
    "tale of custard the dragon|nash": dict(
        grade="6", used="reference", edition="via PoetryVerse",
        stored_ok=False, verify=False,
        note="In US copyright to ~2031. PoetryVerse is an aggregator with no "
             "rights to grant."),
    "do not go gentle into that good night|thomas": dict(
        grade="6", used="reference", edition="Poetry Foundation reprint",
        stored_ok=False, verify=False,
        note="The docx carries its own New Directions credit; that permission "
             "was granted to the Poetry Foundation, not to Optima."),

    # ---------------------------------------------------------------- Grade 7
    "midsummer nights dream|shakespeare": dict(
        grade="7", used="on-page", edition="Project Gutenberg #1514",
        stored_ok=True, verify=False,
        note="9 scene .txt files, 17,058 words, with a _PROVENANCE.md recording "
             "why #1514 was chosen over #2242/#1113/#27761. NOTE: built in "
             "grade 7 but the official book list places it in grade 10."),
    "call of the wild|london": dict(
        grade="7", used="on-page", edition="Project Gutenberg #215",
        stored_ok=True, verify=False, note="Gutenberg boundary markers intact."),
    "christmas carol|dickens": dict(
        grade="7", used="on-page", edition="unattributed 1843 text",
        stored_ok=True, verify=False, note="5 stave PDFs, good text layer."),
    "gullivers travels|swift": dict(
        grade="7", used="on-page", edition="Planet eBook typesetting",
        stored_ok=False, verify=False,
        note="Swift is PD but Planet eBook's layout and in-page branding are "
             "theirs. Part III is MISSING; chapters 1-6 duplicated 5x. Re-set "
             "from Standard Ebooks."),
    "scarlet pimpernel|orczy": dict(
        grade="7", used="on-page", edition="Project Gutenberg #60",
        stored_ok=True, verify=False,
        note="Already rebuilt as 31 Optima-styled reader pages. Best-executed "
             "text in the corpus."),
    "most dangerous game|connell": dict(
        grade="7", used="on-page", edition="Feedbooks edition of the 1924 text",
        stored_ok=False, verify=False,
        note="Text is US PD since 2020, but the FILE carries a Feedbooks notice "
             "reading 'Life+50 countries ... not for commercial purposes'. "
             "Re-source from Wikisource before publishing."),
    "outsiders|hinton": dict(
        grade="7", used="reference", edition="retyped from the book",
        stored_ok=False, verify=False,
        note="8 chapter PDFs with running headers. In copyright to 2062."),

    # ---------------------------------------------------------------- Grade 8
    "emma|austen": dict(
        grade="8", used="on-page", edition="Project Gutenberg (plain text)",
        stored_ok=True, verify=False,
        note="Use the .txt. The sibling PDF's text layer is letter-spaced "
             "garbage ('E m m a  W o o d h o u s e') and needs retyping."),
    "when i heard the learnd astronomer|whitman": dict(
        grade="8", used="on-page", edition="Whitman, 1865",
        stored_ok=True, verify=False, note="Clean 1-page PDF."),
    "anne frank the diary of a young girl|frank": dict(
        grade="8", used="student", edition=None, stored_ok=None, verify=False,
        note="EXEMPLARY. The module states on its cover 'No copyrighted text "
             "from the diary is reproduced', and the organizer spec instructs "
             "'refer to entries by date only'. One gap: "
             "Anne_Frank_Creator_Challenge.pdf is image-only, so it could not "
             "be verified the same way."),
    "out of the silent planet|lewis": dict(
        grade="8", used="reference", edition="Pan Books 1952 of the 1938 text",
        stored_ok=False, verify=False, note="Full 104pp. In copyright."),
    "lord of the flies|golding": dict(
        grade="8", used="reference", edition=None, stored_ok=False, verify=False,
        note="Full 162pp. In copyright."),
    "to kill a mockingbird|lee": dict(
        grade="8", used="reference", edition=None, stored_ok=False, verify=False,
        note="Full 285pp; the file carries its own '(c) renewed 1988' notice."),
    "lottery|jackson": dict(
        grade="8", used="reference", edition="web capture", stored_ok=False,
        verify=False, note="8pp. In copyright."),

    # ---------------------------------------------------------------- Grade 9
    "scarlet letter|hawthorne": dict(
        grade="9", used="on-page", edition="1878 Osgood illustrated edition",
        stored_ok=True, verify=False, note="PD, and a good text layer."),
    "monkeys paw|jacobs": dict(
        grade="9", used="on-page", edition="1902 text", stored_ok=True,
        verify=False, note=None),
    "lady or the tiger|stockton": dict(
        grade="9", used="on-page", edition="1882 text", stored_ok=True,
        verify=False, note=None),
    "sniper|flaherty": dict(
        grade="9", used="on-page", edition="classicshorts.com capture of the 1923 text",
        stored_ok=False, verify=False,
        note="Text is US PD since 2019. Re-set rather than reusing their page "
             "furniture. The copyright review sheet wrongly marks this "
             "in-copyright."),
    "electra|sophocles": dict(
        grade="9", used="reference", edition="E. F. Watling, Penguin Classics",
        stored_ok=False, verify=False,
        note="Watling's translation is (c) 1953 and IN COPYRIGHT; calibre-"
             "converted ebook. Sophocles is PD, this rendering is not. The "
             "review sheet miscategorises it as PD."),
    "canterbury tales|chaucer": dict(
        grade="9", used="reference", edition="Nevill Coghill, Penguin 1951",
        stored_ok=False, verify=False,
        note="Identified from the opening lines ('If there were no authority on "
             "earth / Except experience, mine, for what it's worth'). IN "
             "COPYRIGHT. All five files derive from one pirated ebook."),
    "sir gawain the green knight|": dict(
        grade="9", used="on-page", edition=None, stored_ok=False, verify=True,
        note="TRANSLATOR UNIDENTIFIED. 89pp of body text starting at printed "
             "page 13, with no title page, copyright page, or credit anywhere. "
             "Modern alliterative verse with numbered lines and glosses; not "
             "Tolkien, Armitage, or Borroff by their openings. A PD option "
             "exists (Weston 1898) but it is NOT this text."),
    "crucible|miller": dict(
        grade="9", used="reference", edition=None, stored_ok=False, verify=False,
        note="Full 154pp. In copyright."),
    "secret life of walter mitty|thurber": dict(
        grade="9", used="reference", edition="New Yorker PDF", stored_ok=False,
        verify=False, note="In copyright; magazine layout is a second layer."),
    "there will come soft rains|bradbury": dict(
        grade="9", used="reference", edition="Bradbury, 1950", stored_ok=False,
        verify=False,
        note="In copyright. Distinct from Teasdale's 1920 poem of the same "
             "title, which IS public domain."),
    "dinner party|gardner": dict(
        grade="9", used="reference", edition="scanned commercial worksheet",
        stored_ok=False, verify=True,
        note="The file is a workbook page whose comprehension questions are "
             "separately someone's copyrighted apparatus. 1942 renewal status "
             "unconfirmed."),
    "death by scrabble|fish": dict(
        grade="9", used="reference", edition="Charlie Fish, 2005",
        stored_ok=False, verify=False, note="In copyright."),

    # --------------------------------------------------------------- Grade 10
    "odyssey|homer": dict(
        grade="10", used="on-page", edition="Samuel Butler (PD) for all quotation",
        stored_ok=True, verify=False,
        note="THE PATTERN TO COPY. Every lesson quotes Butler, which is public "
             "domain, while telling students 'Your own copy of The Odyssey "
             "(Fagles translation)'. Optima reproduces no in-copyright text. "
             "Note three documents name three different translations: Butler "
             "(quoted), Fagles (student copy), Fitzgerald (book list)."),
    "oedipus the king oedipus at colonus antigone|sophocles": dict(
        grade="10", used="on-page", edition="F. Storr, Project Gutenberg #31",
        stored_ok=True, verify=False,
        note="Storr 1912 is PD and post-1900, so no archaic flag. The book "
             "list instead names Fitts & Fitzgerald, which is in copyright."),

    # --------------------------------------------------------------- Grade 11
    "hamlet|shakespeare": dict(
        grade="11", used="on-page", edition="unattributed; PD Folger-digitised map",
        stored_ok=True, verify=False, note=None),
    "federalists papers|": dict(
        grade="11", used="on-page", edition="cited by paper number",
        stored_ok=True, verify=False,
        note="Best-aligned title in the whole corpus: all three lists agree, "
             "and the book list links the Library of Congress full text."),
    "selfreliance|emerson": dict(
        grade="11", used="on-page", edition="1841 text, cited by paragraph",
        stored_ok=True, verify=False, note=None),
    "narrative of the life of frederick douglass|douglass": dict(
        grade="11", used="on-page", edition="Project Gutenberg #23",
        stored_ok=True, verify=False, note="Cited by chapter."),

    # --------------------------------------------------------------- Grade 12
    "bhagavad gita|": dict(
        grade="12", used="on-page", edition="Sir Edwin Arnold, 1885",
        stored_ok=True, verify=False,
        note="OLDER band (1850-99). Credited on the page, unlike the book list."),
    "bible|": dict(
        grade="12", used="on-page", edition="King James Version, 1611",
        stored_ok=True, verify=False, note=None),
    "confucian analects|": dict(
        grade="12", used="on-page", edition="Lionel Giles, 1907",
        stored_ok=True, verify=False, note=None),
    "buddhist parables|": dict(
        grade="12", used="on-page", edition="Eugene Watson Burlingame",
        stored_ok=True, verify=True,
        note="The lesson credits 1923; Buddhist Legends (Harvard Oriental "
             "Series) is 1921. Either way PD, but the year should be settled."),
    "nicomachean ethics|aristotle": dict(
        grade="12", used="on-page", edition="D. P. Chase",
        stored_ok=True, verify=True,
        note="ARCHAIC band. Chase is 1847, which trips the pre-1850 flag - the "
             "only live Optima translation that does. A revised edition is "
             "cited 1877; which one is in use decides the tier."),
    "frankenstein|shelley": dict(
        grade="12", used="on-page", edition="1818 text", stored_ok=True,
        verify=False, note=None),
    "excerpts from nietzsches writings|": dict(
        grade="12", used="on-page",
        edition="Common (Zarathustra) / Zimmern (BGE) / H. B. Samuel (Genealogy)",
        stored_ok=True, verify=False,
        note="All three PD and post-1900 (1909, 1906, 1913). Far more precise "
             "than the book list's 'excerpts from Nietzsche's writings'."),
    "heart of darkness|conrad": dict(
        grade="12", used="on-page", edition="1899 text", stored_ok=True,
        verify=False, note=None),
    "metamorphosis|kafka": dict(
        grade="12", used="student", edition=None, stored_ok=None, verify=False,
        note="Reproduces no translation. The lesson tells students to 'check "
             "how your edition renders it', which sidesteps the rights "
             "question the way the Odyssey does."),
    "republic allegory of the cave|plato": dict(
        grade="12", used="on-page", edition=None, stored_ok=None, verify=True,
        note="TRANSLATOR UNNAMED. The page says only 'Public domain English "
             "text. Excerpt.' The PD claim rests on nothing checkable."),
    "quran|": dict(
        grade="12", used="on-page", edition=None, stored_ok=None, verify=True,
        note="TRANSLATOR UNNAMED for Suras 1 and 112. Rodwell (1861) would be "
             "PD; Yusuf Ali (1934) would not. The page cannot tell you which."),
}

# Works taught in built coursework that appear on NO list. Real gaps in the
# official book list, found by auditing the courses.
NOT_ON_BOOKLIST = [
    ("Sonnets 18, 29, 116, 130", "William Shakespeare", "9",
     "Built as clean typed PDFs; absent from the official book list entirely."),
    ("Ulysses", "Alfred, Lord Tennyson", "10 Honors", "1842; built, unlisted."),
    ("Poetics", "Aristotle", "10 Honors",
     "Built with NO translator credited anywhere - unverifiable as PD."),
    ("Patrick Henry's 1775 speech", "Patrick Henry", "11", "Built, unlisted."),
    ("Meditations", "Marcus Aurelius", "12",
     "George Long (1862), OLDER band. Built, unlisted."),
    ("God's Grandeur", "Gerard Manley Hopkins", "12", "Published 1918. Built, unlisted."),
    ("A Shropshire Lad", "A. E. Housman", "12", "1896. Built, unlisted."),
    ("The Collar", "George Herbert", "12", "1633. Built, unlisted."),
    ("The Tyger", "William Blake", "12", "1794. Built, unlisted."),
    ("Hope is the thing with feathers", "Emily Dickinson", "12",
     "First published 1891. Built, unlisted."),
]


def self_test():
    bad = []
    for k, v in COURSE.items():
        if "|" not in k:
            bad.append(f"malformed key: {k!r}")
        if v.get("used") not in ("on-page", "student", "reference"):
            bad.append(f"{k}: bad 'used' value {v.get('used')!r}")
        if v.get("used") == "student" and v.get("stored_ok") is not None:
            bad.append(f"{k}: 'student' should have stored_ok=None")
        if not v.get("grade"):
            bad.append(f"{k}: no grade")
    if bad:
        for b in bad:
            print("  FAIL:", b)
        raise SystemExit(f"course_editions self-test failed ({len(bad)})")

    from collections import Counter
    used = Counter(v["used"] for v in COURSE.values())
    ver = [k for k, v in COURSE.items() if v["verify"]]
    prob = [k for k, v in COURSE.items()
            if v["stored_ok"] is False and v["used"] == "on-page"]
    print(f"course_editions self-test: OK  ({len(COURSE)} taught titles)")
    print(f"   reproduced on-page : {used['on-page']}")
    print(f"   student's own copy : {used['student']}")
    print(f"   reference only     : {used['reference']}")
    print(f"   not on any list    : {len(NOT_ON_BOOKLIST)}")
    print(f"\n   {len(ver)} title(s) needing a human check:")
    for k in ver:
        print(f"      {k}")
    print(f"\n   {len(prob)} on-page text(s) with a file problem:")
    for k in prob:
        print(f"      {k}")


if __name__ == "__main__":
    self_test()
