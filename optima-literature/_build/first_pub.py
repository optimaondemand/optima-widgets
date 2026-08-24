"""
first_pub.py — curated first-publication data for the Optima corpus.

WHY THIS FILE EXISTS
Open Library cannot supply first-publication dates. Its `first_publish_date` is
edition metadata and returns nonsense for old works (January 17 2007 for Dante,
1588 for Sophocles' Electra, January 1999 for the Odyssey). Google Books, the
natural cross-check, is quota-blocked. So the dates that the rights logic and the
pre-1850 translation flag depend on are curated here, by hand, and marked with a
confidence level.

CONFIDENCE
  "high"   - standard, uncontroversial date
  "verify" - a real ambiguity worth a human check before anyone leans on it.
             These surface in the widget as a VERIFY flag rather than silently
             passing as fact.

DATE CONVENTIONS
  year        int, negative for BC (-375 == c. 375 BC)
  circa       True when the year is approximate (ancient and medieval works)
  lang        original language. "en" suppresses the archaic-translation flag
              entirely, per the rule: never flag a work written in English,
              however old, because there the old English IS the text.

KEYS match _build/parse_sources.py joinkey(): normalised title (leading article
stripped) + "|" + author surname, lowercased. Author-less works use an empty
surname, e.g. "bible|".
"""

# ---------------------------------------------------------------- works
# key: (year, circa, lang, confidence, note)
WORKS = {
    # ---- Grade 6
    "adventures of robin hood|green":      (1956, False, "en", "high", None),
    "bronze bow|speare":                   (1961, False, "en", "high", None),
    "king arthur and his knights of the round table|green":
                                           (1953, False, "en", "high", None),
    "st george and the dragon|lotti":      (2014, False, "en", "high", None),
    "arabian nights|henaff":               (2007, False, "en", "verify",
                                            "Tarnowska retelling; retelling date, not the Nights"),
    "golden touch|hawthorne":              (1851, False, "en", "high",
                                            "in A Wonder-Book for Girls and Boys"),
    "tale of custard the dragon|nash":     (1936, False, "en", "high", None),
    "scarlet ibis|hurst":                  (1960, False, "en", "high", None),
    "retrieved reformation|henry":         (1903, False, "en", "high", None),
    "do not go gentle into that good night|thomas":
                                           (1951, False, "en", "high",
                                            "In Country Sleep; (c) 1939/1946 New Directions per credit line"),
    "tales from shakespeare|lamb":         (1807, False, "en", "high", None),
    "charles|jackson":                     (1948, False, "en", "high", None),
    "if|kipling":                          (1910, False, "en", "high", None),

    # ---- Grade 7
    "gullivers travels|swift":             (1726, False, "en", "high", None),
    "christmas carol|dickens":             (1843, False, "en", "high", None),
    "outsiders|hinton":                    (1967, False, "en", "high", None),
    "most dangerous game|connell":         (1924, False, "en", "high",
                                            "Collier's, 19 Jan 1924; US PD 1 Jan 2020"),
    "scarlet pimpernel|orczy":             (1905, False, "en", "high", None),
    "landlady|dahl":                       (1959, False, "en", "high", None),
    "call of the wild|london":             (1903, False, "en", "high", None),

    # ---- Grade 8
    "emma|austen":                         (1815, False, "en", "high", None),
    "romeo and juliet|shakespeare":        (1597, True,  "en", "high", "first quarto"),
    "out of the silent planet|lewis":      (1938, False, "en", "high", None),
    "lord of the flies|golding":           (1954, False, "en", "high", None),
    "to kill a mockingbird|lee":           (1960, False, "en", "high", None),
    "when i heard the learnd astronomer|whitman":
                                           (1865, False, "en", "high", "Drum-Taps"),
    "anne frank the diary of a young girl|frank":
                                           (1947, False, "nl", "high",
                                            "Dutch 1947; first English translation 1952"),
    "lottery|jackson":                     (1948, False, "en", "high", "The New Yorker"),

    # ---- Grade 9
    "electra|sophocles":                   (-410, True,  "grc", "high", None),
    "taming of the shrew|shakespeare":     (1594, True,  "en", "high", None),
    "beowulf|":                            (1000, True,  "ang", "verify",
                                            "MS c.1000; composition date disputed, 8th-11th c."),
    "scarlet letter|hawthorne":            (1850, False, "en", "high", None),
    "canterbury tales|chaucer":            (1400, True,  "enm", "high", "unfinished at death"),
    "divine comedy|alighieri":             (1320, True,  "it", "high", None),
    "secret life of walter mitty|thurber": (1939, False, "en", "high", "The New Yorker"),
    "road not taken|frost":                (1916, False, "en", "high", "Mountain Interval"),
    "sir gawain the green knight|":      (1400, True,  "enm", "high", None),
    "monkeys paw|jacobs":                  (1902, False, "en", "high", None),
    "lady or the tiger|stockton":          (1882, False, "en", "high", None),
    "sniper|flaherty":                    (1923, False, "en", "high",
                                            "The New Leader; US PD 1 Jan 2019"),
    "dinner party|gardner":                (1942, False, "en", "verify",
                                            "Saturday Review 1942; US renewal status unconfirmed"),
    "there will come soft rains|bradbury": (1950, False, "en", "high",
                                            "Bradbury story; NOT the 1920 Teasdale poem of the same title"),
    "death by scrabble|fish":              (2005, False, "en", "high", None),
    "crucible|miller":                     (1953, False, "en", "high", None),

    # ---- Grade 10
    "odyssey|homer":                       (-725, True,  "grc", "verify",
                                            "8th c. BC, conventionally; oral composition"),
    "once and future king|white":          (1958, False, "en", "high", None),
    "things fall apart|achebe":            (1958, False, "en", "high", None),
    "julius caesar|shakespeare":           (1599, False, "en", "high", None),
    "oedipus the king oedipus at colonus antigone|sophocles":
                                           (-429, True,  "grc", "high",
                                            "Oedipus Tyrannus c.429 BC; the three plays are not a trilogy"),
    "of mice and men|steinback":           (1937, False, "en", "high",
                                            "booklist misspells Steinbeck"),
    "midsummer nights dream|shakespeare":  (1595, True,  "en", "high", None),
    "great gatsby|fitzgerald":             (1925, False, "en", "high", "US PD 1 Jan 2021"),
    "animal farm|orwell":                  (1945, False, "en", "high", None),
    "night|wiesel":                        (1956, False, "yi", "high",
                                            "Yiddish 1956; French 1958; English 1960"),
    "red badge of courage|crane":          (1895, False, "en", "high", None),
    "o captain my captain|whitman":        (1865, False, "en", "high", None),
    "things they carried|brian":          (1990, False, "en", "high",
                                            "booklist misspells O'Brien"),
    "war that is finished|ford":           (1975, False, "en", "high",
                                            "US government work, not under copyright"),
    "their eyes were watching god|hurston":(1937, False, "en", "high",
                                            "IN COPYRIGHT to 2033; review sheet wrongly marks PD"),
    "harrison bergeron|vonnegut":          (1961, False, "en", "high", None),

    # ---- Grade 11
    "fahrenheit 451|bradbury":             (1953, False, "en", "high", None),
    "brave new world|huxley":              (1932, False, "en", "high", None),
    "grapes of wrath|steinbeck":           (1939, False, "en", "high", None),
    "legend of sleepy hollow and rip van winkle|irving":
                                           (1819, False, "en", "high",
                                            "The Sketch Book, 1819-20"),
    "narrative of the life of frederick douglass|douglass":
                                           (1845, False, "en", "high", None),
    "handmaids tale|atwood":               (1985, False, "en", "high", None),
    "adventures of huckleberry finn|twain": (1884, False, "en", "high",
                                            "UK 1884; US 1885"),
    "selected poems|dickinson":            (1890, False, "en", "high",
                                            "first posthumous collection"),
    "hamlet|shakespeare":                  (1603, True,  "en", "high",
                                            "Q1 1603, Q2 1604"),
    "selfreliance|emerson":               (1841, False, "en", "high", "Essays: First Series"),
    "federalists papers|":                 (1788, False, "en", "high", "1787-88"),
    "great expectations|dickens":          (1861, False, "en", "high", None),
    "jane eyre|bront":                     (1847, False, "en", "high", None),
    "romantic poets|":                     (1798, True,  "en", "verify",
                                            "collection; Wordsworth-Keats span c.1798-1821"),

    # ---- Grade 12
    "brothers karamazov|dostoevsky":       (1880, False, "ru", "high", None),
    "heart of darkness|conrad":            (1899, False, "en", "high",
                                            "Blackwood's 1899; book 1902"),
    "metamorphosis|kafka":                 (1915, False, "de", "high", None),
    "1984|orwell":                         (1949, False, "en", "high", None),
    "one hundred years of solitude|rquez": (1967, False, "es", "high", None),
    "slaughterhousefive|vonnegut":        (1969, False, "en", "high", None),
    "invisible man|ellison":               (1952, False, "en", "high", None),
    "wise blood|connor":                  (1952, False, "en", "high", None),
    "frankenstein|shelley":                (1818, False, "en", "high",
                                            "1818 first ed.; 1831 revised"),
    "fellowship of the ring|tolkien":      (1954, False, "en", "high", None),
    "aeneid|virgil":                       (-19,  True,  "la", "high",
                                            "unfinished at Virgil's death, 19 BC"),
    "road|mccarthy":                       (2006, False, "en", "high", None),
    "room of ones own|woolf":              (1929, False, "en", "high", "US PD 1 Jan 2025"),
    "waste land|eliot":                    (1922, False, "en", "high", "US PD"),
    "waiting for godot|beckett":           (1952, False, "fr", "high",
                                            "French 1952; Beckett's own English 1954"),
    "little prince|exupery":               (1943, False, "fr", "high", None),
    "little prince|exup":         (1943, False, "fr", "high", None),
    "hero with a thousand faces|campbell": (1949, False, "en", "high", None),
    "republic allegory of the cave|plato":                      (-375, True,  "grc", "high", None),
    "nicomachean ethics|aristotle":        (-340, True,  "grc", "high", None),
    "bible|":                              (1611, False, "mul", "verify",
                                            "composite; 1611 is the KJV translation, not the text"),
    "bhagavad gita|":                      (-200, True,  "sa", "verify",
                                            "c. 200 BC - 200 AD; disputed"),
    "quran|":                                (632,  True,  "ar", "high",
                                            "7th c.; canonical recension shortly after 632"),
    "quran|":                              (632,  True,  "ar", "high", None),
    "buddhist parables|":                  (400,  True,  "pi", "verify",
                                            "Pali canon commentarial tradition; span is wide"),
    "confucian analects|":                 (-400, True,  "lzh", "verify",
                                            "compiled c. 475-221 BC"),
    "excerpts from nietzsches writings|":  (1883, True,  "de", "verify",
                                            "spans 1872-1888; depends on selection"),
}

# ------------------------------------------------------- translations in use
# Keyed by translator surname, lowercased. `year` is the TRANSLATION's first
# publication, which is what the archaic-language flag keys off -- never the
# work's date.
TRANSLATIONS = {
    # named by the official book list
    "fitzgerald":  {"name": "Robert Fitzgerald", "year": 1961, "conf": "high",
                    "note": "Odyssey 1961; Iliad 1974"},
    "fitts":       {"name": "Dudley Fitts", "year": 1949, "conf": "high",
                    "note": "with Robert Fitzgerald, Oedipus Rex"},
    "heaney":      {"name": "Seamus Heaney", "year": 1999, "conf": "high", "note": None},
    "ciardi":      {"name": "John Ciardi", "year": 1954, "conf": "verify",
                    "note": "Inferno 1954, Purgatorio 1961, Paradiso 1970"},
    "coghill":     {"name": "Nevill Coghill", "year": 1951, "conf": "high", "note": None},
    "watling":     {"name": "E. F. Watling", "year": 1953, "conf": "high", "note": None},

    # public-domain translations actually used in built Optima coursework
    "butler":      {"name": "Samuel Butler", "year": 1900, "conf": "high",
                    "note": "prose Odyssey; exactly on the 1900 boundary"},
    "storr":       {"name": "F. Storr", "year": 1912, "conf": "high",
                    "note": "Loeb; Gutenberg #31"},
    "chase":       {"name": "D. P. Chase", "year": 1847, "conf": "verify",
                    "note": "ARCHAIC BAND. 1847 first ed.; a revised ed. is cited 1877 "
                            "-- which one Gutenberg carries decides the flag tier"},
    "arnold":      {"name": "Sir Edwin Arnold", "year": 1885, "conf": "high",
                    "note": "The Song Celestial"},
    "giles":       {"name": "Lionel Giles", "year": 1907, "conf": "high", "note": None},
    "burlingame":  {"name": "Eugene Watson Burlingame", "year": 1921, "conf": "verify",
                    "note": "Buddhist Legends, Harvard Oriental Series 1921; "
                            "12th-grade lesson credits 1923"},
    "common":      {"name": "Thomas Common", "year": 1909, "conf": "high",
                    "note": "Thus Spake Zarathustra"},
    "zimmern":     {"name": "Helen Zimmern", "year": 1906, "conf": "high",
                    "note": "Beyond Good and Evil"},
    "samuel":      {"name": "Horace B. Samuel", "year": 1913, "conf": "high",
                    "note": "Genealogy of Morals"},
    "long":        {"name": "George Long", "year": 1862, "conf": "high",
                    "note": "Meditations"},
    "weston":      {"name": "Jessie L. Weston", "year": 1898, "conf": "high",
                    "note": "Sir Gawain; the PD option, NOT what the 9th-grade folder holds"},
    "jowett":      {"name": "Benjamin Jowett", "year": 1871, "conf": "high",
                    "note": "Plato"},
}

# Language codes whose works are ORIGINALLY English. The archaic flag never
# applies to these, however old, because the old English is the text itself.
ENGLISH_ORIGINAL = {"en", "enm", "ang"}


def flag_tier(translation_year, original_language):
    """
    The house rule, in one place:
      English original, any date  -> no flag, ever
      translation pre-1850        -> "archaic"  (amber warning)
      translation 1850-1899       -> "older"    (neutral, shown not warned)
      translation 1900+           -> none       (preferred band)
    """
    if original_language in ENGLISH_ORIGINAL:
        return "none"
    if translation_year is None:
        return "unknown"
    if translation_year < 1850:
        return "archaic"
    if translation_year < 1900:
        return "older"
    return "none"


def self_test():
    """Both directions, per house rule: assert what should AND should not flag."""
    cases = [
        # (translation_year, lang, expected)
        (1847, "grc", "archaic"),   # Chase Aristotle
        (1862, "grc", "older"),     # Long Meditations
        (1885, "sa",  "older"),     # Arnold Gita
        (1898, "enm", "none"),      # Weston Gawain -- Middle English original
        (1900, "grc", "none"),      # Butler, exactly on the boundary
        (1912, "grc", "none"),      # Storr
        (1961, "grc", "none"),      # Fitzgerald
        (None, "grc", "unknown"),
        (1600, "en",  "none"),      # Shakespeare: English, never flagged
        (1726, "en",  "none"),      # Swift: English, never flagged
        (1000, "ang", "none"),      # Beowulf original: Old English, not flagged
    ]
    bad = []
    for yr, lang, want in cases:
        got = flag_tier(yr, lang)
        if got != want:
            bad.append(f"flag_tier({yr},{lang!r}) = {got!r}, want {want!r}")
    # keys must be parseable and unique
    for k in WORKS:
        if "|" not in k:
            bad.append(f"malformed WORKS key: {k!r}")
    verify = [k for k, v in WORKS.items() if v[3] == "verify"]
    if bad:
        for b in bad:
            print("  FAIL:", b)
        raise SystemExit(f"first_pub self-test failed: {len(bad)} problem(s)")
    print(f"first_pub self-test: OK  "
          f"({len(WORKS)} works, {len(TRANSLATIONS)} translations, "
          f"{len(verify)} flagged VERIFY)")
    for k in verify:
        print(f"   VERIFY  {k:52} {WORKS[k][4] or ''}")


if __name__ == "__main__":
    self_test()
