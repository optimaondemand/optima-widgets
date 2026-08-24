"""
genres.py — genre for every record, harvested rather than invented.

None of the three source lists carries a genre. The student Independent Reading
library already has one (13 shelves, used for its genre cards), so we harvest
that taxonomy instead of inventing a second one -- two widgets over one corpus
must not disagree about what shelf a book is on.

Titles the student library does not carry (mostly K-5 picture books) fall back
to a small curated map, then to form ("poem", "play", "short story"), then to
"Unclassified" so the gap is visible rather than papered over.
"""
import ast
import json
import re
from pathlib import Path

IR_DATA = Path(r"C:\Users\JessicaDrexel\OneDrive - OptimaEd\ELA"
               r"\_independent-reading\reading_bank_data.py")

# Frozen copy of the harvest, taken from the last build made with the student
# library present (2026-08-24). Used only when reading_bank_data.py is not on
# this machine, so a rebuild elsewhere does not silently unshelve 112 titles.
SNAPSHOT = Path(__file__).resolve().parent / "genre_snapshot.json"

# The student library splits Classics/Epic-Drama-Poetry per band and uses two
# near-duplicate names. Collapse to one shelf name per concept.
CANON = {
    "Myth, Legend & Epic": "Myth, Legend & Folklore",
    "Epic, Drama & Poetry": "Drama & Poetry",
    "Science & Mathematics (excerpt reading)": "Nonfiction & Biography",
}

SHELF_ART = {
    "Classics":                        ("&#127963;", "#8E6BB5"),
    "Myth, Legend & Folklore":         ("&#128009;", "#C7922C"),
    "Mystery, Adventure & Humor":      ("&#128269;", "#2E9E8F"),
    "Fantasy & Science Fiction":       ("&#128640;", "#3D7BD9"),
    "Historical Fiction":              ("&#8987;",   "#B4703A"),
    "Nonfiction & Biography":          ("&#128240;", "#5A7089"),
    "Drama & Poetry":                  ("&#127917;", "#C25B6B"),
    "Novels & Literary Fiction":       ("&#128214;", "#8E6BB5"),
    "Philosophy, Politics & Theology": ("&#9878;",   "#4A6FA5"),
    "American Founding & Documents":   ("&#128220;", "#B4703A"),
    "Picture Books & Early Readers":   ("&#127752;", "#2E9E8F"),
    "Unclassified":                       ("&#128218;", "#6b7a99"),
}

# Curated only where the student library has no entry. Kept short on purpose:
# every line here is a judgement, and a wrong shelf is worse than "Unclassified".
CURATED = {
    "scarlet ibis|hurst":                  "Novels & Literary Fiction",
    "retrieved reformation|henry":          "Mystery, Adventure & Humor",
    "charles|jackson":                      "Novels & Literary Fiction",
    "landlady|dahl":                        "Mystery, Adventure & Humor",
    "dinner party|gardner":                 "Novels & Literary Fiction",
    "death by scrabble|fish":               "Mystery, Adventure & Humor",
    "secret life of walter mitty|thurber":  "Mystery, Adventure & Humor",
    "sniper|oflaherty":                     "Historical Fiction",
    "war that is finished|ford":            "American Founding & Documents",
    "federalists papers|":                  "American Founding & Documents",
    "self-reliance|emerson":                "Philosophy, Politics & Theology",
    "bible|":                               "Philosophy, Politics & Theology",
    "qurn|":                                "Philosophy, Politics & Theology",
    "quran|":                               "Philosophy, Politics & Theology",
    "bhagavad gita|":                       "Philosophy, Politics & Theology",
    "buddhist parables|":                   "Philosophy, Politics & Theology",
    "confucian analects|":                  "Philosophy, Politics & Theology",
    "republic|plato":                       "Philosophy, Politics & Theology",
    "nicomachean ethics|aristotle":         "Philosophy, Politics & Theology",
    "excerpts from nietzsches writings|":   "Philosophy, Politics & Theology",
    "room of ones own|woolf":               "Nonfiction & Biography",
    "hero with a thousand faces|campbell":  "Nonfiction & Biography",
    "anne frank the diary of a young girl|frank": "Nonfiction & Biography",
}

FORM_FALLBACK = {
    "poem": "Drama & Poetry",
    "play": "Drama & Poetry",
    "short story": "Novels & Literary Fiction",
    "short story collection": "Novels & Literary Fiction",
    "speech": "American Founding & Documents",
    "multi-author collection": "Novels & Literary Fiction",
}


def _key(title, author):
    """Mirror of parse_sources.joinkey."""
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


def harvest_from_ir():
    """
    Parse the student library's data module with ast (never exec) and pull
    title|author -> shelf out of its per-band genre dicts.
    """
    if not IR_DATA.exists():
        if SNAPSHOT.exists():
            print(f"  NOTE: {IR_DATA.name} not found; using {SNAPSHOT.name}")
            return json.loads(SNAPSHOT.read_text(encoding="utf8"))
        print(f"  NOTE: {IR_DATA.name} not found; genre harvest skipped")
        return {}
    tree = ast.parse(IR_DATA.read_text(encoding="utf8"))
    out = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        for k, v in zip(node.keys, node.values):
            if not (isinstance(k, ast.Constant) and isinstance(k.value, str)):
                continue
            shelf = CANON.get(k.value, k.value)
            if shelf not in SHELF_ART:
                continue
            if not isinstance(v, ast.List):
                continue
            for item in v.elts:
                if not isinstance(item, ast.Tuple) or len(item.elts) < 2:
                    continue
                a, b = item.elts[0], item.elts[1]
                if not (isinstance(a, ast.Constant) and isinstance(b, ast.Constant)):
                    continue
                out.setdefault(_key(str(a.value), str(b.value)), shelf)
    return out


_IR_CACHE = None


def genre_for(title, author, kind=None, grade=None):
    global _IR_CACHE
    if _IR_CACHE is None:
        _IR_CACHE = harvest_from_ir()
    k = _key(title, author)
    if k in _IR_CACHE:
        return _IR_CACHE[k], "student-library"
    if k in CURATED:
        return CURATED[k], "curated"
    if grade in ("K", "1", "2"):
        return "Picture Books & Early Readers", "grade-default"
    if kind and kind in FORM_FALLBACK:
        return FORM_FALLBACK[kind], "form"
    return "Unclassified", "none"


def self_test():
    h = harvest_from_ir()
    print(f"harvested {len(h)} title->shelf pairs from the student library")
    shelves = {}
    for v in h.values():
        shelves[v] = shelves.get(v, 0) + 1
    for s, n in sorted(shelves.items(), key=lambda x: -x[1]):
        print(f"   {n:4}  {s}")
    bad = [s for s in shelves if s not in SHELF_ART]
    assert not bad, f"harvested unknown genre names: {bad}"
    # spot checks in both directions
    g, src = genre_for("Emma", "Jane Austen")
    print(f"\n   Emma -> {g} ({src})")
    g2, src2 = genre_for("Zzz Nonexistent Book", "Nobody")
    assert g2 == "Unclassified", g2
    print(f"   unknown title -> {g2} ({src2})  [correct]")
    print("genres self-test: OK")


if __name__ == "__main__":
    self_test()
