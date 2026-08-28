# -*- coding: utf-8 -*-
"""course_additions.py -- titles a course teaches that are NOT on the book list.

library.json has always carried a `taught_but_on_no_list` list: works the
coursework uses that the official .docx never mentions (Tennyson's Ulysses,
Patrick Henry's speech, several Grade 12 poems). Until now that was a note in
the manifest and nothing more -- no card, so a teacher looking for one of those
titles in this library found nothing and had no way to tell whether it was
missing or simply unlisted.

This module is where such a title becomes a real card. A record here:

  * has a real Optima grade, unlike the CLT layer's sentinel "CLT"
  * has `listed_as: None`, because the book list does not name it -- the card
    says so in as many words rather than letting a teacher assume a family can
    buy it off the approved list
  * is Taught if and only if course_editions.py says a course teaches it. That
    table stays the single authority for the Taught badge; nothing here sets it.

Everything else -- date, genre, CLT badge -- resolves through the normal keyed
tables, so a record here behaves exactly like a book-list record apart from the
one fact that differs.
"""

ADDITIONS = [
    {
        "grade": "10",
        "listed_as": None,          # not on the OAO 2026-27 book list
        "title": "Macbeth",
        "author": "William Shakespeare",
        "authors": None,
        "kind": "play",
        "edition_hint": None,
        "notes": [],
        # No purchase edition: the text is public domain and the free link is
        # the whole point. A buy button here would send a family shopping for
        # something the course hands them.
        "url": None,
        "url_kind": None,
        "asin": None,
        "extra_urls": [],
        "listed_count": 0,
        "key": "macbeth|shakespeare",
        "review": None,
        "edition": {},
        "free_version": {
            # Gutenberg #1533 is the id Optima's own Independent Reading build
            # already resolved for this play (_independent-reading pd_links.json),
            # so the two libraries point at the same text.
            "state": "identical",   # English original, public domain
            "reason": None,
            "free": {
                "url": "https://www.gutenberg.org/ebooks/1533",
                "source": "gutenberg.org",
                "gutenberg_id": 1533,
                "matched_title": "Macbeth",
                "via": "course-additions",
            },
            "read_online": {
                # The Folger edition is the one most classrooms cite by
                # through-line number. Linked, never presented as a download.
                "url": "https://www.folger.edu/explore/shakespeares-works/macbeth/",
                "source": "folger.edu",
            },
            "note": None,
        },
        "not_on_book_list": True,
    },
]
