# -*- coding: utf-8 -*-
"""Render gate for music-reference-library.html.

Run from optima-music/:   python _build/probe_render.py

A data gate proves the numbers are right. It proves nothing about whether the page
paints: the whole grid is built by script, so one exception during boot ships a page
with an empty shelf and every data assertion still passing. This loads the built file in
headless Chrome and asserts the DOM that actually appeared.

Four traps this harness is written around, all of which have bitten before:

1. Use a real Windows path. Git Bash's pwd returns /c/..., Chrome loads an error page,
   and every count reads 0 -- a false failure that looks exactly like a real one.
2. Strip <script> before counting. The renderer's own source contains the same class
   strings it emits, so matching the raw dump inflates every count.
3. grep -c counts LINES; generated innerHTML is one long line. Count matches.
4. Give Chrome a unique --user-data-dir, or a running browser makes it exit silently.
"""
import os, re, sys, json, subprocess, tempfile, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PAGE = os.path.join(ROOT, "music-reference-library.html")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# Videos that must never appear on the published page, named here by id.
#
# Deliberately NOT read from the generator's WITHDRAWN list. The rest of this probe does
# read that list, which means it checks the page against the generator's intent -- and
# would happily pass if someone deleted a withdrawal, because the expectation would
# vanish with it. This list is the independent one: removing an entry from here is a
# visible act, not a side effect.
NEVER_PUBLISH = {
    "wxp3xSkbVRU": '"Gabriela" Dance Break Version (KATSEYE), withdrawn 2026-09-01',
}


def dump():
    if not os.path.exists(CHROME):
        sys.exit("chrome not found at " + CHROME)
    profile = tempfile.mkdtemp(prefix="musiclib-probe-")
    cmd = [CHROME, "--headless", "--disable-gpu", "--no-sandbox",
           "--user-data-dir=" + profile, "--virtual-time-budget=9000",
           "--allow-file-access-from-files", "--dump-dom",
           "file:///" + PAGE.replace("\\", "/")]
    r = subprocess.run(cmd, capture_output=True, timeout=180)
    out = r.stdout.decode("utf-8", "replace")
    if len(out) < 5000:
        sys.exit("chrome returned %d bytes; stderr:\n%s"
                 % (len(out), r.stderr.decode("utf-8", "replace")[:2000]))
    return out


def main():
    contract = json.load(open(os.path.join(ROOT, "music.json"), encoding="utf-8"))
    # The generator withholds some videos from the published page. Read that list out of
    # the generator itself rather than restating it here, so the two cannot drift.
    sys.path.insert(0, HERE)
    # importing is safe: the generator only builds under __main__
    from build_music_library import WITHDRAWN
    videos = [v for v in contract["videos"] if v["id"] not in WITHDRAWN]
    withheld = [v for v in contract["videos"] if v["id"] in WITHDRAWN]
    doc = dump()

    # trap 2: everything inside a <script> is the renderer, not the render
    painted = re.sub(r"<script.*?</script>", "", doc, flags=re.S)
    # trap 3 handled by findall throughout
    grid = re.search(r'<div class="grid" id="grid">(.*?)</div></main>', painted, re.S)
    grid = grid.group(1) if grid else ""

    fails = []

    def eq(got, want, what):
        if got != want:
            fails.append("%s: got %d, expected %d" % (what, got, want))

    def has(needle, what):
        if needle not in painted:
            fails.append("missing from the rendered page: " + what)

    n = lambda pat, hay=None: len(re.findall(pat, grid if hay is None else hay))

    # ---- the shelf painted at all
    if not grid:
        fails.append("the grid container did not render; nothing else can be trusted")
    eq(n(r'<article class="card" data-id='), len(videos), "cards in the grid")
    eq(n(r'class="empty"'), 0, "empty-state blocks (the grid should not be empty)")

    # ---- a dead video gets no player, and a live one does
    dead = [v for v in videos if v["state"] != "ok"]
    eq(n(r'class="noframe"'), len(dead), "dead-link frames")
    eq(n(r'class="playbtn"'), len(videos) - len(dead), "play buttons")
    eq(n(r'youtube-nocookie\.com/embed/', grid), 0,
       "embeds in the grid before anything is clicked (nothing should preload)")

    # ---- the build-bookkeeping badges are gone from the cards on purpose
    eq(n(r'<span class="badge '), 0,
       'status badges on cards ("In use" and friends were removed)')
    # a dead link still has to say so, as a warning rather than a status
    eq(n(r'<p class="warn">'), len(dead), "dead-link warnings")

    # ---- default order. Badge counts could never see ORDER, and the first build shipped
    # a "Suggested" sort that put every dropped and legacy video above the 141 in-use
    # ones, because rank["in-use"] was 0 and `0 || 4` is 4 in JS. With the badges gone the
    # anchor is the card id, which also makes the assertion exact rather than approximate.
    # Assert the PROPERTY, not a reproduced sort. Within a rank the page orders by
    # localeCompare on a normalised title, and Python's str.lower() cannot reproduce that
    # -- a title opening with a curly quote sorts under G in the browser and after Z in
    # Python. Chasing that would test the collation, not the page. What matters is that
    # the rank sequence never goes backwards.
    rank = {"in-use": 1, "live-canvas": 2, "dropped-in-renovation": 3, "unknown": 4,
            "dead-link": 5}
    by_id = {v["id"]: v for v in videos}
    got = re.findall(r'<article class="card" data-id="([^"]+)"', grid)
    unknown = [i for i in got if i not in by_id]
    if unknown:
        fails.append("cards for videos not in the contract: " + ", ".join(unknown[:3]))
    seq = [rank.get(by_id[i]["disposition"], 4) for i in got if i in by_id]
    for i in range(1, len(seq)):
        if seq[i] < seq[i - 1]:
            fails.append("default order goes backwards at card %d: rank %d follows rank %d"
                         % (i, seq[i], seq[i - 1]))
            break
    if seq and seq[0] != 1:
        fails.append("default order does not open with an in-use video")
    if dead and seq[-len(dead):] != [5] * len(dead):
        fails.append("dead links are not last in the default order")

    # ---- citations, topics, cross-refs
    eq(n(r'<details class="uses">'), sum(1 for v in videos if v["lessons"]),
       "lesson citation blocks")
    eq(n(r'<span class="pill'), sum(len(v["tags"]) for v in videos), "topic pills")
    eq(n(r'Also in the art library'), sum(1 for v in videos if v["cross_refs"].get("art")),
       "art cross-reference blocks")
    eq(n(r'Also in the ELA library'), sum(1 for v in videos if v["cross_refs"].get("ela")),
       "ELA cross-reference blocks")
    eq(n(r'Module not recorded'),
       sum(1 for v in videos for l in v["lessons"] if l["module"] is None),
       "module-not-recorded citations")

    # ---- controls. Counted inside their own select, not across the document.
    def sel(sid):
        m = re.search(r'<select id="' + sid + r'".*?</select>', painted, re.S)
        return m.group(0) if m else ""
    courses_drawn = sum(1 for c in contract["courses"]
                        if any(c["id"] in v["courses"] for v in videos))
    eq(n(r'<option', sel("course")), 0,
       "leftover course dropdown (it was replaced by browse chips)")
    topics = {(t["scheme"], t["code"]) for v in videos for t in v["tags"]}
    eq(n(r'<option', sel("topic")), len(topics) + 1, "topic options (plus All)")
    eq(n(r'<optgroup', sel("topic")),
       len({s for s, c in topics}), "topic groups")
    eq(n(r'<option', sel("sort")), 4, "sort options")
    # NOT class="chip: the container is class="chips" and matches the same prefix, which
    # is how this probe once reported 5 chips for 4. Count the data attribute instead.
    eq(n(r'data-status="', painted), 1, "the dead-link chip")
    eq(n(r'data-xref="', painted), 2, "cross-library chips")

    # ---- the independent never-publish check (see NEVER_PUBLISH above)
    for vid, why in NEVER_PUBLISH.items():
        if vid in doc:
            fails.append("a video that must never be published is on the page: " + vid +
                         " -- " + why)

    # ---- the two browse axes
    genres = {t["code"] for v in videos for t in v["tags"]
              if t["scheme"] == "music.genre"}
    eq(n(r'data-course="', painted), courses_drawn, "course browse chips")
    eq(n(r'data-genre="', painted), len(genres), "genre browse chips")
    has("Browse by course", "the course browse label")
    has("Browse by genre", "the genre browse label")

    # ---- a withdrawn video must be gone from the page entirely: not as a card, not in
    # the inlined data, not in a hover title. This is what makes the withdrawal real
    # rather than cosmetic.
    for v in withheld:
        if v["id"] in doc:
            fails.append("withheld video id is still in the page: " + v["id"])
        # The whole title, not single words: "Version" and "Beautiful" appear in other
        # videos' titles, and a word-by-word check failed on those instead of on the
        # withdrawal. The id check above is the strong one -- every card and every data
        # record is keyed by it.
        if (v["title"] or "") and (v["title"] in grid or v["title"] in
                                   re.sub(r"<script.*?</script>", "", doc, flags=re.S)
                                   .split('id="panel"')[0]):
            fails.append("a withheld video's title is still on the shelf: " + v["id"])
    if withheld and "Withheld from this catalogue" not in painted:
        fails.append("videos were withheld but the panel does not record it")

    # ---- the things a teacher must not miss
    has("links no longer play", "the dead-link notice")
    for v in dead:
        has(v["id"], "dead video " + v["id"] + " named in the panel")
    has('id="named-not-linked"', "the named-but-not-linked section")
    prompts = {(p["course"], p.get("module"), p["query"])
               for p in contract["search_prompts"]}
    eq(n(r'youtube\.com/results\?', painted), len(prompts), "search links for named pieces")

    # ---- tray
    for bid in ("traycopy", "trayembed", "trayclear", "traycount"):
        has('id="' + bid + '"', "tray control " + bid)

    # ---- probes: known records, so a page that paints 155 of the WRONG thing fails
    for probe in ("Music and creativity in Ancient Greece",
                  "TED-Ed", "Ode to Joy"):
        has(probe, "probe record " + probe)

    print("render gate: %d failures" % len(fails))
    for f in fails:
        print("  FAIL: " + f)
    if fails:
        sys.exit(1)
    print("  %d cards, %d pills, %d citations painted"
          % (n(r'<article class="card" data-id='), n(r'<span class="pill'),
             n(r'<details class="uses">')))


if __name__ == "__main__":
    main()
