# -*- coding: utf-8 -*-
"""Generate music-reference-library.html from music.json.

Run from optima-music/:   python _build/build_music_library.py

music.json is the contract, written by _build/build_contract.py in
    OneDrive - OptimaEd\\Claude's Workshop\\Music Library
which holds the harvest of the nine music course build folders, the oEmbed liveness
pass, and the evidence-gated tagging. This generator never invents a fact: if a video
is attributed to one course rather than four, it is because the contract says so.

NEVER HAND-EDIT THE HTML. It is overwritten on every run, and a hand-edit would also
bypass the gate at the bottom of this file.
"""
import os, sys, json, html, collections, re, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from music_library_css import CSS
from music_library_js import JS

# Reuse the official wordmark already embedded for the ELA and art libraries rather than
# carrying a third copy of the same base64. All three pages sit in this repo.
LOGO_SRC = os.path.join(os.path.dirname(ROOT), "optima-literature", "_build",
                        "brand_assets.py")

# Videos withheld from the published catalogue by editorial decision.
#
# This list lives HERE and not in the workshop's contract builder on purpose. The contract
# is a truthful record of what the courses actually link, and a harvest that denied a
# video the course still embeds would be a lie. This page is what students and teachers
# browse, which is a different question. Filtering here also means re-emitting the
# contract cannot quietly bring a withdrawn video back.
#
# Withdrawing a video from the catalogue does NOT remove it from the course. Anything in
# this list that has a course chip is still embedded in that course's build folder and
# needs pulling there separately.
WITHDRAWN = {
    "wxp3xSkbVRU": "Withdrawn on request, 2026-09-01. Still present in the Music "
                   "Intermediate I build folder.",
}

# Badge labels for the course chips on a card. Short enough to sit in a pill, and taken
# from what the builds themselves are called: the MI-1/2/3 folders, "M/J Music Theory".
# The full course name is always in the chip's hover text.
SHORT = {
    "music-k": "Music K", "music-1": "Music 1", "music-2": "Music 2",
    "mi-1": "MI-1", "mi-2": "MI-2", "mi-3": "MI-3",
    "mt-1": "Theory 1", "mt-2": "Theory 2",
    "motw": "Music of the World",
}

# Group headings for the one topic control. Eight schemes as eight <optgroup>s beats
# eight separate selects across the top of the page.
SCHEME_GROUPS = [
    ("music.genre", "Genre"),
    ("music.era", "Era"),
    ("music.composer", "Composer"),
    ("music.culture", "Culture or tradition"),
    ("music.element", "Element of music"),
    ("music.instrument", "Instrument"),
    ("music.skill", "Skill"),
    ("concept", "Cross-subject"),
]

WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday",
            "saturday", "sunday")


def load_logo():
    ns = {}
    with open(LOGO_SRC, encoding="utf-8") as f:
        exec(compile(f.read(), LOGO_SRC, "exec"), ns)
    return ns["OAO_LOGO"]


def e(s):
    return html.escape("" if s is None else str(s), quote=True)


def build():
    contract = json.load(open(os.path.join(ROOT, "music.json"), encoding="utf-8"))

    held = [v for v in contract["videos"] if v["id"] in WITHDRAWN]
    contract["videos"] = [v for v in contract["videos"] if v["id"] not in WITHDRAWN]
    for v in held:
        print("withheld: " + v["id"] + "  " + (v["title"] or "")[:60])
    missing = set(WITHDRAWN) - {v["id"] for v in held}
    if missing:
        # A withdrawal that matches nothing is either a typo or a video the harvest has
        # already lost. Either way it must not pass silently.
        sys.exit("withdrawal list names ids that are not in the contract: " +
                 ", ".join(sorted(missing)))

    videos = contract["videos"]
    courses = contract["courses"]

    # Presentation-only addition: a short badge label per course. It is added to the copy
    # of the contract that goes into the page, never written back to music.json.
    for c in courses:
        c["short"] = SHORT.get(c["id"], c["id"])

    cmap = {c["id"]: c for c in courses}
    n_use = sum(1 for v in videos if v["disposition"] == "in-use")
    n_dead = sum(1 for v in videos if v["state"] != "ok")
    per_course = collections.Counter(c for v in videos for c in v["courses"])
    drawn = sum(1 for c in courses if per_course[c["id"]])
    n_art = sum(1 for v in videos if v["cross_refs"].get("art"))
    n_ela = sum(1 for v in videos if v["cross_refs"].get("ela"))

    # topic counts, by scheme:code, over videos rather than over tags: a video tagged
    # both "violin" and "cello" must count once in each, not twice in either.
    topic_n = collections.Counter()
    topic_label = {}
    for v in videos:
        for key in {(t["scheme"], t["code"]) for t in v["tags"]}:
            topic_n[key] += 1
        for t in v["tags"]:
            topic_label[(t["scheme"], t["code"])] = t["label"]
    genre_codes = {code for sch, code in topic_n if sch == "music.genre"}

    # the pieces a lesson names but never links, deduped and put in course/module order
    prompts, seen = [], set()
    for p in contract["search_prompts"]:
        key = (p["course"], p.get("module"), p["query"])
        if key in seen:
            continue
        seen.add(key)
        prompts.append(p)
    prompts.sort(key=lambda p: (cmap[p["course"]]["short"] if p["course"] in cmap
                                else p["course"],
                                -1 if p.get("module") is None else p["module"],
                                p["query"].lower()))

    parts = []
    A = parts.append
    A("<!doctype html>")
    A('<html lang="en"><head><meta charset="utf-8">')
    A('<meta name="viewport" content="width=device-width,initial-scale=1">')
    A("<title>Optima Music Reference Library</title>")
    A('<meta name="description" content="Every video used across the Optima music '
      'courses, with what it is, which module uses it, and whether the link still works.">')
    A("<style>" + CSS + "</style>")
    A("</head><body>")

    # ---------------- hero ----------------
    A('<header class="hero"><div class="wrap">')
    A('<div class="brandrow"><img src="' + load_logo() + '" alt="Optima Academy Online">')
    A('<div class="rule"></div><h1>Music Reference Library</h1></div>')
    A('<p class="sub">Every video used across the nine Optima music courses, in one '
      'place. Browse by course or by genre, or search a composer, an instrument or a '
      'title. Each record says which course and module it belongs to, and whether the '
      'link still plays. Videos are linked, never re-hosted.</p>')
    A('<div class="statline">')
    # The old second stat counted videos "in a rebuilt module", which is build
    # bookkeeping: true, and meaningless to anyone browsing for something to listen to.
    # The two browse axes belong here instead.
    A('<div class="stat"><b>' + str(len(videos)) + "</b><span>Videos catalogued</span></div>")
    A('<div class="stat"><b>' + str(drawn) + "</b><span>Courses</span></div>")
    A('<div class="stat live"><b>' + str(len(genre_codes)) + "</b><span>Genres</span></div>")
    A('<div class="stat gap"><b>' + str(len(prompts)) + '</b>'
      '<button type="button" id="gapjump">Named but not linked</button></div>')
    A("</div></div></header>")

    # ---------------- controls ----------------
    A('<section class="controls"><div class="wrap">')
    A('<div class="searchrow">')
    A('<div class="searchbox"><span class="mag">&#9906;</span>')
    A('<input id="q" type="search" autocomplete="off" placeholder="Search title, '
      'channel, composer, course&hellip;" aria-label="Search the catalogue"></div>')

    A('<select id="topic" aria-label="Filter by topic">')
    A('<option value="">All topics</option>')
    for scheme, heading in SCHEME_GROUPS:
        rows = sorted(((k, n) for k, n in topic_n.items() if k[0] == scheme),
                      key=lambda kn: (-kn[1], topic_label[kn[0]].lower()))
        if not rows:
            continue
        A('<optgroup label="' + e(heading) + '">')
        for (sch, code), n in rows:
            A('<option value="' + e(sch + ":" + code) + '">' +
              e(topic_label[(sch, code)]) + " (" + str(n) + ")</option>")
        A("</optgroup>")
    A("</select>")

    A('<select id="sort" aria-label="Sort">'
      '<option value="default">Suggested</option>'
      '<option value="uses">Most used</option>'
      '<option value="title">Title A&ndash;Z</option>'
      '<option value="channel">Channel A&ndash;Z</option></select>')
    A('<button class="gearbtn" id="gear" type="button" '
      'aria-label="How this catalogue was built">&#9881; How this was built</button>')
    A("</div>")

    # ---- browse by course. Chips rather than a dropdown: the nine courses are the first
    # question anyone brings to this page, and a shelf you can see is a shelf you browse.
    # Only courses with videos get a chip; a chip that filters to nothing is not a shelf.
    A('<div class="browse">')
    A('<span class="lab">Browse by course</span>')
    for c in courses:
        n = per_course[c["id"]]
        if not n:
            continue
        A('<button class="chip" type="button" data-course="' + e(c["id"]) + '" '
          'aria-pressed="false" title="' + e(c["name"] + " · " + c["code"]) + '">' +
          e(c["short"]) + '<span class="n">' + str(n) + "</span></button>")
    A("</div>")

    # ---- browse by genre
    genre_rows = sorted(((code, n) for (sch, code), n in topic_n.items()
                         if sch == "music.genre"),
                        key=lambda cn: (-cn[1], topic_label[("music.genre", cn[0])].lower()))
    A('<div class="browse">')
    A('<span class="lab">Browse by genre</span>')
    for code, n in genre_rows:
        A('<button class="subj" type="button" data-genre="' + e(code) + '" '
          'aria-pressed="false">' + e(topic_label[("music.genre", code)]) +
          '<span class="n">' + str(n) + "</span></button>")
    A("</div>")

    A('<div class="subjects">')
    A('<span class="lab">Also</span>')
    A('<button class="subj gold" type="button" data-status="dead-link" '
      'aria-pressed="false">Link no longer works<span class="n">' + str(n_dead) +
      "</span></button>")
    A('<button class="subj" type="button" data-xref="art" aria-pressed="false">'
      'In the art library<span class="n">' + str(n_art) + "</span></button>")
    A('<button class="subj" type="button" data-xref="ela" aria-pressed="false">'
      'In the ELA library<span class="n">' + str(n_ela) + "</span></button>")
    A("</div>")

    A('<p class="resultline" id="resultline"></p>')

    # The one thing a teacher must not miss, and the only gold on the page.
    if n_dead:
        still = sorted({cmap[c]["short"] for v in videos if v["state"] != "ok"
                        for c in v["courses"] if c in cmap})
        A('<div class="notice"><b>' + str(n_dead) + ' of these links no longer play.</b> '
          'They are still embedded in ' + e(", ".join(still)) + ', so a student meets a '
          'blank frame where a lesson expects a video. Filter to '
          '<code>Link no longer works</code> to see which, and where.</div>')

    # ---------------- panel ----------------
    A('<section class="panel" id="panel">')
    A("<h2>How this catalogue was built</h2>")
    A("<p>" + e(contract["purpose"]) + "</p>")

    A("<h3>Which course teaches a video</h3>")
    A("<p>" + e(contract["legacy_note"]) + " A chip on a card is therefore evidence from "
      "a rebuilt module, not from an export. Where a video is that course's own live "
      "Canvas content and the course has no rebuilt folder yet, the chip is outlined "
      "rather than solid.</p>")

    A("<h3>What a topic tag claims</h3>")
    A("<p>" + e(contract["scope_note"]) + " Hover any tag to read the exact string that "
      "justified it. A dashed outline marks a tag that describes the lesson rather than "
      "the video.</p>")

    A("<h3>Where each video stands</h3>")
    A("<table><tr><th>Status</th><th>Videos</th><th>What it means</th></tr>")
    MEANING = {
        "in-use": "Cited by a lesson page in a rebuilt build folder.",
        "live-canvas": "That course's own live Canvas content; the course has no rebuilt "
                       "folder yet.",
        "dropped-in-renovation": "In the old export, in no rebuilt module. Available to "
                                 "reuse, not currently taught.",
        "dead-link": "Deleted or made private on YouTube since it was linked.",
        "unknown": "Not traced to a course.",
    }
    for code, n in sorted(contract["counts"]["dispositions"].items(),
                          key=lambda kv: -kv[1]):
        A("<tr><td>" + e(code) + '</td><td class="num">' + str(n) + "</td><td>" +
          e(MEANING.get(code, "")) + "</td></tr>")
    A("</table>")

    A("<h3>Per course</h3>")
    A("<table><tr><th>Course</th><th>Code</th><th>Grade</th><th>Videos</th>"
      "<th>Evidence</th></tr>")
    for c in courses:
        n = per_course[c["id"]]
        if c["has_build"] and n:
            ev = "Rebuilt build folder harvested."
        elif c["has_build"]:
            # Theory 2 is the case: the folder exists and was read, and its lessons link
            # no video at all. "Harvested" beside a zero reads as a harvest failure.
            ev = "Rebuilt folder harvested; its lessons link no video."
        elif n:
            ev = "No rebuilt folder yet; videos come from the live Canvas export."
        else:
            ev = "No rebuilt folder yet, and its export shares the cloned pool, so "\
                 "nothing can be attributed to it."
        A("<tr><td>" + e(c["name"]) + "</td><td><code>" + e(c["code"]) + "</code></td><td>" +
          e(c["grade"]) + '</td><td class="num">' + str(n) + "</td><td>" + e(ev) +
          "</td></tr>")
    A("</table>")

    A("<h3>Links that no longer play</h3>")
    A("<table><tr><th>Video</th><th>State</th><th>Still linked from</th></tr>")
    for v in sorted(videos, key=lambda v: v["state"]):
        if v["state"] == "ok":
            continue
        where = ", ".join(cmap[c]["short"] for c in v["courses"] if c in cmap) or \
                "no rebuilt module"
        A("<tr><td><code>" + e(v["id"]) + "</code></td><td>" + e(v["state"]) +
          "</td><td>" + e(where) + "</td></tr>")
    A("</table>")

    A("<h3>Browsing by genre</h3>")
    n_genre = sum(1 for v in videos
                  if any(t["scheme"] == "music.genre" for t in v["tags"]))
    A("<p>The genre shelves cover <b>" + str(n_genre) + " of " + str(len(videos)) +
      "</b> videos across " + str(len(genre_codes)) + " genres. The rest carry no genre "
      "because nothing in their record names one &mdash; a lesson page called "
      "&ldquo;Rhythm in Detail&rdquo; says what the video teaches, not what kind of "
      "music it is. Those videos are still reachable by course, by search, and by the "
      "other topic filters.</p>")

    A("<h3>Topic coverage</h3>")
    scheme_n = collections.Counter()
    for v in videos:
        for scheme in {t["scheme"] for t in v["tags"]}:
            scheme_n[scheme] += 1
    A("<table><tr><th>Scheme</th><th>Values used</th><th>Videos carrying one</th></tr>")
    for scheme, heading in SCHEME_GROUPS:
        vals = len({k for k in topic_n if k[0] == scheme})
        if not vals:
            continue
        A("<tr><td>" + e(heading) + ' <code>' + e(scheme) + '</code></td><td class="num">' +
          str(vals) + '</td><td class="num">' + str(scheme_n[scheme]) + "</td></tr>")
    A("</table>")
    untagged = sum(1 for v in videos if not v["tags"])
    A("<p>" + str(len(videos) - untagged) + " of " + str(len(videos)) +
      " videos carry at least one topic. A tag is attached only when a harvested string "
      "&mdash; the video title, the channel, or the title of the lesson page using it "
      "&mdash; contains wording that names the idea. Musical knowledge never counts: a "
      "Brandenburg concerto is a lesson in counterpoint, but if nothing in the record "
      "says so, it carries no such tag.</p>")

    A('<h3 id="named-not-linked">Named in a lesson, never linked (' +
      str(len(prompts)) + ")</h3>")
    A("<p>These are pieces an Optima music lesson tells a student to find, with no video "
      "linked for them. Each row is a real gap: the lesson names the work, the "
      "catalogue has nothing to hand a teacher. The search link opens YouTube with the "
      "wording the lesson itself uses.</p>")
    A('<div class="scroll"><table><tr><th>Course</th><th>Module</th><th>Piece the '
      "lesson names</th><th></th></tr>")
    for p in prompts:
        c = cmap.get(p["course"])
        q = urllib.parse.urlencode({"search_query": p["query"]})
        A("<tr><td>" + e(c["short"] if c else p["course"]) + '</td><td class="num">' +
          (e(p["module"]) if p.get("module") is not None else "&mdash;") + "</td><td>" +
          e(p["query"]) + '</td><td><a href="https://www.youtube.com/results?' + e(q) +
          '" target="_blank" rel="noopener">Search</a></td></tr>')
    A("</table></div>")

    if held:
        A("<h3>Withheld from this catalogue</h3>")
        A("<p>" + str(len(held)) + (" video is" if len(held) == 1 else " videos are") +
          " withheld from this page by editorial decision. Withholding a video here does "
          "not remove it from a course: where it is still in a build folder, that is "
          "recorded below and needs pulling separately.</p>")
        A("<table><tr><th>Video</th><th>Why</th></tr>")
        for v in held:
            A("<tr><td>" + e(v["title"] or v["id"]) + "</td><td>" +
              e(WITHDRAWN[v["id"]]) + "</td></tr>")
        A("</table>")

    A("<h3>What is not stored here</h3>")
    A("<p>Titles, channels, thumbnails and links only. No lyrics and no transcripts are "
      "held anywhere in this catalogue or its build kit &mdash; Optima links out to "
      "music rather than reproducing it. Nothing loads from YouTube until you press "
      "play, and the player is the <code>youtube-nocookie</code> embed, so browsing "
      "this shelf does not build a watch history.</p>")

    A("<h3>Provenance</h3>")
    A("<p>Generated " + e(contract["generated"]) + " from <code>music.json</code>, which "
      "is emitted by <code>_build/build_contract.py</code> in Claude&rsquo;s Workshop "
      "&rarr; Music Library. This page is built by "
      "<code>_build/build_music_library.py</code> and is overwritten on every run; edit "
      "the generator, never the HTML.</p>")
    A("</section>")
    A("</div></section>")

    # ---------------- grid + tray ----------------
    A('<main class="wrap"><div class="grid" id="grid"></div></main>')
    A('<div class="tray" id="tray" role="region" aria-label="Listening list">'
      '<div class="wrap">')
    A('<div class="count" id="traycount"></div>')
    A('<div class="names" id="traynames"></div>')
    A('<button type="button" id="trayclear">Clear</button>')
    A('<button type="button" id="trayembed">Copy Canvas embed</button>')
    A('<button type="button" class="primary" id="traycopy">Copy listening list</button>')
    A("</div></div>")
    A('<footer class="wrap">Optima Academy Online &middot; Music Reference Library. '
      "Every video is linked from its own channel, never copied; a channel can remove a "
      "video at any time, so check a link before you rely on it.</footer>")

    blob = json.dumps(contract, ensure_ascii=False, separators=(",", ":"))
    # a title containing </script> would end the block early; escaping the slash keeps
    # the JSON valid and the parser inside the string
    A("<script>var MUSIC=" + blob.replace("</", "<\\/") + ";</script>")
    A("<script>" + JS + "</script>")
    A("</body></html>")

    doc = "\n".join(parts)
    out = os.path.join(ROOT, "music-reference-library.html")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(doc)

    gate(doc, contract, prompts)
    print("wrote " + out)
    print("  " + format(len(doc.encode("utf-8")), ",") + " bytes  |  " +
          str(len(videos)) + " videos, " + str(n_use) + " in use, " +
          str(n_dead) + " dead, " + str(len(prompts)) + " named-not-linked")
    return out


def gate(doc, contract, prompts):
    """Fail the build rather than ship a page that misstates what is taught where."""
    fails = []
    videos = contract["videos"]
    labels = contract["labels"]

    def check(cond, msg):
        if not cond:
            fails.append(msg)

    # ---- structure
    check(doc.count("<html") == 1 and doc.rstrip().endswith("</html>"),
          "malformed document")
    check(doc.count("<style") == 1, "expected exactly one style block")
    check(doc.count("<script") == 2, "expected exactly two script blocks")
    check("preview-banner" not in doc, "a preview banner leaked into the page")

    # ---- house rules, on my prose only. Video titles are data: a video legitimately
    # called "Sunday Morning" must not fail the weekday rule, and a channel could name
    # anything at all.
    chrome = re.sub(r"<script>.*?</script>", "", doc, flags=re.S)
    check("facilitator" not in chrome.lower(), "the word facilitator appears; say teacher")
    for d in WEEKDAYS:
        if re.search(r"\b" + d + r"\b", chrome, re.I):
            fails.append("a weekday appears in the page's own prose: " + d)
    for machine in ("Source Harvest", "2-dot-1-expressive-qualities.html"):
        check(machine not in chrome, "a harvester string leaked into visible prose: " +
              machine)

    # ---- links
    for v in videos:
        if not v["url"].startswith("https://www.youtube.com/watch?v="):
            fails.append("watch url is not a youtube watch link: " + v["id"])
        if not v["embed_url"].startswith("https://www.youtube-nocookie.com/embed/"):
            fails.append("embed url is not the nocookie host: " + v["id"])
    check("youtube-nocookie.com/embed/" in doc, "no nocookie embeds in the page")
    check("youtube.com/embed/" not in doc.replace("youtube-nocookie.com/embed/", ""),
          "a cookie-setting youtube embed leaked in")

    # ---- no prose, no lyrics. The contract carries titles and page titles, both short;
    # a transcript or a lesson body would show up immediately as a long string.
    def longest(o, path="videos"):
        worst = (0, path)
        if isinstance(o, str):
            return (len(o), path)
        if isinstance(o, dict):
            for k, val in o.items():
                worst = max(worst, longest(val, path + "/" + k))
        elif isinstance(o, list):
            for val in o:
                worst = max(worst, longest(val, path + "/[]"))
        return worst
    n, where = longest(videos)
    check(n <= 220, "a long string is in the video records (%d chars at %s): prose or a "
                    "transcript may have leaked" % (n, where))

    # Field NAMES, not substrings. Three of these videos are legitimately called
    # "Official Lyric Video" by their own channels, and an earlier version of this check
    # grepped the whole blob and failed on the data it exists to protect.
    def keys(o):
        if isinstance(o, dict):
            for k, val in o.items():
                yield k
                for kk in keys(val):
                    yield kk
        elif isinstance(o, list):
            for val in o:
                for kk in keys(val):
                    yield kk
    # Scoped to the video records: the vocabularies are keyed by CODE, and one of those
    # codes is legitimately "texture".
    for k in set(keys(videos)):
        for banned in ("transcript", "lyric", "prose", "body"):
            if banned in k.lower():
                fails.append("a video record carries a field named " + k)
    ALLOWED = {"id", "url", "embed_url", "title", "channel", "channel_url", "thumb",
               "state", "disposition", "courses", "attribution", "legacy_in", "lessons",
               "tags", "cross_refs"}
    for v in videos:
        extra = set(v) - ALLOWED
        if extra:
            fails.append("unexpected field on " + v["id"] + ": " + ", ".join(sorted(extra)))

    # ---- attribution honesty: the whole reason the contract exists
    for v in videos:
        if v["attribution"] == "build" and not v["courses"]:
            fails.append("build attribution with no course: " + v["id"])
        if v["attribution"] == "legacy-pool" and v["courses"]:
            fails.append("legacy-pool video attributed to a course: " + v["id"])
        if v["attribution"] == "live-canvas" and not v["courses"]:
            fails.append("live-canvas attribution with no course: " + v["id"])
        if v["disposition"] == "in-use" and v["attribution"] != "build":
            fails.append("in-use without build evidence: " + v["id"])

    # ---- a dead link must look dead
    for v in videos:
        if v["state"] != "ok":
            if v["disposition"] != "dead-link":
                fails.append("unusable video not marked dead-link: " + v["id"])
            if v["thumb"]:
                fails.append("dead video still carries a thumbnail: " + v["id"])
        elif not v["title"]:
            fails.append("live video with no resolved title: " + v["id"])

    # ---- every tag must carry its evidence and its scope, or the hover text lies
    for v in videos:
        for t in v["tags"]:
            if not t.get("asserted_by"):
                fails.append("tag with no evidence: " + v["id"] + " / " + t["code"])
            if t.get("scope") not in ("video", "lesson"):
                fails.append("tag with no scope: " + v["id"] + " / " + t["code"])
            if t["scheme"] == "concept":
                if not t.get("discipline"):
                    fails.append("concept tag with no discipline: " + v["id"])
                if t["code"] not in contract["concept_vocabulary"]:
                    fails.append("concept outside the vocabulary: " + t["code"])
            else:
                want = labels.get(t["scheme"], {}).get(t["code"])
                if want is None:
                    fails.append("tag outside its vocabulary: " + t["scheme"] + ":" +
                                 t["code"])
                elif want != t["label"]:
                    fails.append("tag label disagrees with the vocabulary: " + t["code"])

    # ---- cross-library links. Same rule as the art library: an image must come from the
    # assets repo, because several museums 403 a github.io referer.
    for v in videos:
        for h in v["cross_refs"].get("art", []):
            if h.get("image") and not h["image"].startswith(
                    "https://optimaondemand.github.io/optima-art-assets/"):
                fails.append("art cross-ref image not on the assets host: " + h["id"])

    # ---- the page must actually say the numbers it claims
    check(">" + str(len(videos)) + "</b><span>Videos catalogued" in doc,
          "hero video count does not match the contract")
    check(">" + str(len(prompts)) + "</b>" in doc,
          "hero named-not-linked count does not match the deduped list")
    n_courses = sum(1 for c in contract["courses"]
                    if any(c["id"] in v["courses"] for v in videos))
    check(chrome.count('<option value="') >= n_courses,
          "course options missing from the filter")

    print("gate: " + str(len(fails)) + " failures")
    for f in fails:
        print("  FAIL: " + f)
    if fails:
        sys.exit(1)


if __name__ == "__main__":
    build()
