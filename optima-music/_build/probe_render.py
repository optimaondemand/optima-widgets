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


INTERACT = """
<script>
(function(){
  // Drive the real controls and write what happened into the DOM, where --dump-dom can
  // see it. Nothing here reaches into the renderer's closure: it clicks and types.
  var out = [];
  function say(k, v){ out.push(k + "=" + v); }
  try {
    var card = document.querySelector('.card .clipbtn');
    if (!card) throw new Error("no clip button rendered");
    var id = card.dataset.clipbtn;
    var art = document.querySelector('.card[data-id="' + id + '"]');
    say("id", id);
    var row = art.querySelector('.cliprow');
    // computed, not the attribute: a display rule on the row can override [hidden]
    say("row_display_before", getComputedStyle(row).display);
    card.click();
    say("row_open", !row.hidden);
    say("row_display_after", getComputedStyle(row).display);
    var sIn = row.querySelector('[data-clip-start]'), eIn = row.querySelector('[data-clip-end]');
    // a bad range first: the end before the start
    sIn.value = "2:05"; eIn.value = "1:20";
    eIn.dispatchEvent(new Event("change", {bubbles: true}));
    say("err_order", row.querySelector('.cliperr').textContent);
    // then a good one
    sIn.value = "1:20"; eIn.value = "2:05";
    eIn.dispatchEvent(new Event("change", {bubbles: true}));
    say("err_ok", row.querySelector('.cliperr').textContent);
    say("btn", art.querySelector('.clipbtn').textContent);
    say("btn_set", art.querySelector('.clipbtn').classList.contains("set"));
    say("watch", art.querySelector('.watch').getAttribute("href"));
    say("clear_shown", !row.querySelector('.clipclear').hidden);
    // not a time
    sIn.value = "one twenty";
    sIn.dispatchEvent(new Event("change", {bubbles: true}));
    say("err_text", row.querySelector('.cliperr').textContent);
    // restore the good clip, then play: the iframe must carry it
    sIn.value = "1:20";
    sIn.dispatchEvent(new Event("change", {bubbles: true}));
    art.querySelector('.playbtn').click();
    var fr = art.querySelector('.frame iframe');
    say("iframe", fr ? fr.getAttribute("src") : "none");
    // clear: the button and link go back to their unset state
    row.querySelector('.clipclear').click();
    say("btn_after_clear", art.querySelector('.clipbtn').textContent);
    say("watch_after_clear", art.querySelector('.watch').getAttribute("href"));
    say("iframe_after_clear", art.querySelector('.frame iframe').getAttribute("src"));
  } catch (e) { say("exception", e.message); }
  var pre = document.createElement("pre"); pre.id = "probe-out";
  pre.textContent = out.join("\\n");
  document.body.appendChild(pre);
})();
</script>
"""


def interact():
    """Second Chrome run against a copy of the page with a driver script appended."""
    src = open(PAGE, encoding="utf-8").read()
    tmpdir = tempfile.mkdtemp(prefix="musiclib-interact-")
    path = os.path.join(tmpdir, "page.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(src.replace("</body></html>", INTERACT + "</body></html>"))
    profile = tempfile.mkdtemp(prefix="musiclib-probe-")
    cmd = [CHROME, "--headless", "--disable-gpu", "--no-sandbox",
           "--user-data-dir=" + profile, "--virtual-time-budget=9000",
           "--allow-file-access-from-files", "--dump-dom",
           "file:///" + path.replace("\\", "/")]
    r = subprocess.run(cmd, capture_output=True, timeout=180)
    out = r.stdout.decode("utf-8", "replace")
    m = re.search(r'<pre id="probe-out">(.*?)</pre>', out, re.S)
    if not m:
        return {"exception": "driver wrote nothing"}
    got = {}
    for line in m.group(1).split("\n"):
        if "=" in line:
            k, v = line.split("=", 1)
            got[k.strip()] = v.rstrip('\r\n')  # Chrome on Windows ends dump lines with CRLF
    return got


def main():
    contract = json.load(open(os.path.join(ROOT, "music.json"), encoding="utf-8"))
    # The generator withholds some videos from the published page. Read that list out of
    # the generator itself rather than restating it here, so the two cannot drift.
    sys.path.insert(0, HERE)
    # importing is safe: the generator only builds under __main__
    from build_music_library import WITHDRAWN, SCHEME_GROUPS
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

    # ---- clip controls: one row and one button per live card, none on a dead one, every
    # row collapsed on a fresh load, and the end field carries the running time
    live_n = len(videos) - len(dead)
    eq(n(r'data-cliprow="'), live_n, "clip rows")
    eq(n(r'<div class="cliprow" data-cliprow="[^"]+" hidden(="")?>'), live_n,
       "clip rows collapsed on first load")
    eq(n(r'data-clipbtn="'), live_n, "clip buttons")
    eq(n(r'>Set a clip</button>'), live_n, "clip buttons in their unset state")
    eq(n(r'data-clip-start="'), live_n, "clip start fields")
    eq(n(r'data-clip-end="'), live_n, "clip end fields")
    eq(n(r'<span class="cliplen">of \d+:\d\d'),
       sum(1 for v in videos if v["state"] == "ok" and v.get("duration")),
       "running-time labels")
    for v in dead:
        if re.search(r'data-clipbtn="' + re.escape(v["id"]) + '"', grid):
            fails.append("a dead video offers a clip button: " + v["id"])

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
    rank = {"in-use": 1, "live-canvas": 2, "previous-version": 3, "unknown": 4,
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
    # lesson.topic tags are deliberately not pills: the labels are whole lesson titles
    eq(n(r'<span class="pill'),
       sum(1 for v in videos for t in v["tags"] if t["scheme"] != "lesson.topic"),
       "topic pills")
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
    # only the schemes the dropdown is built from: kind has a browse row of its own and
    # lesson.topic labels are entire lesson titles
    in_menu = {s for s, _ in SCHEME_GROUPS}
    topics = {(t["scheme"], t["code"]) for v in videos for t in v["tags"]
              if t["scheme"] in in_menu}
    eq(n(r'<option', sel("topic")), len(topics) + 1, "topic options (plus All)")
    eq(n(r'<optgroup', sel("topic")),
       len({s for s, c in topics}), "topic groups")
    eq(n(r'<option', sel("sort")), 4, "sort options")
    # NOT class="chip: the container is class="chips" and matches the same prefix, which
    # is how this probe once reported 5 chips for 4. Count the data attribute instead.
    eq(n(r'data-status="', painted), 1, "the dead-link chip")
    eq(n(r'data-xref="', painted), 2, "cross-library chips")

    # ---- no downloadable copy anywhere on the page. Independent of the generator's
    # DOWNLOADS dict on purpose, like NEVER_PUBLISH: as of 2026-09-11 nothing in the
    # catalogue may be re-hosted, and adding a hosted file must be a visible change here.
    eq(n(r'class="dl"', painted), 0, "download links")
    eq(n(r'<a [^>]*\sdownload[\s>=]', painted), 0, "anchors with a download attribute")
    eq(n(r'\.mp4', painted), 0, "mp4 references")

    # ---- the independent never-publish check (see NEVER_PUBLISH above)
    for vid, why in NEVER_PUBLISH.items():
        if vid in doc:
            fails.append("a video that must never be published is on the page: " + vid +
                         " -- " + why)

    # ---- the two browse axes
    genres = {t["code"] for v in videos for t in v["tags"]
              if t["scheme"] == "music.genre"}
    kinds = {t["code"] for v in videos for t in v["tags"]
             if t["scheme"] == "video.kind"}
    eq(n(r'data-course="', painted), courses_drawn, "course browse chips")
    eq(n(r'data-genre="', painted), len(genres), "genre browse chips")
    eq(n(r'data-kind="', painted), len(kinds), "kind browse chips")
    has("Browse by course", "the course browse label")
    has("Browse by genre", "the genre browse label")
    has("Browse by kind", "the kind browse label")

    # ---- dates and piece notes actually reach the cards
    eq(n(r'<p class="dates">'), sum(1 for v in videos
                                    if v.get("work_year") or v.get("recording_year")),
       "date lines")
    if dead:
        has("No link on YouTube", "the no-link wording on a removed video")
    # a removed video's entry must still say what the piece was
    for v in dead:
        if not v.get("piece_note"):
            fails.append("removed video with no piece note: " + v["id"])

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
    # The page no longer carries an audit trail -- the builder panel went with the rest
    # of the build bookkeeping -- so the id check above is the whole assertion here. The
    # reason a video was withheld lives in WITHDRAWN and the README.

    # ---- the things nobody must miss
    if dead:
        has("no longer on YouTube", "the removed-video notice")

    # ---- getting back out of a filter. Filters persist in localStorage, so without a
    # reset the first chip click changed the view for good -- which is what happened.
    has('id="reset"', "the reset control")
    if 'id="reset"' in painted and 'id="reset" type="button" hidden' not in painted             and "hidden" not in re.search(r'<button[^>]*id="reset"[^>]*>', painted).group(0):
        fails.append("the reset control is visible with no filter active")
    if "×" not in doc and "\00D7" not in doc:
        fails.append("active chips carry no dismiss mark, so nothing says they toggle off")

    # ---- tray
    for bid in ("traycopy", "trayembed", "trayclear", "traycount"):
        has('id="' + bid + '"', "tray control " + bid)

    # ---- probes: known records, so a page that paints 155 of the WRONG thing fails
    for probe in ("Music and creativity in Ancient Greece",
                  "TED-Ed", "Ode to Joy"):
        has(probe, "probe record " + probe)

    # ---- clip controls, driven. The static counts above prove the controls painted;
    # this proves they do what the card says: an invalid range is refused with a reason,
    # a valid one reaches the button, the watch link and the player, and Clear undoes it.
    got = interact()
    by_id = {v["id"]: v for v in videos}
    if "exception" in got:
        fails.append("clip driver: " + got["exception"])
    else:
        vid = got.get("id", "")
        v = by_id.get(vid)
        amp = lambda s: (s or "").replace("&amp;", "&")
        if got.get("row_display_before") != "none":
            fails.append("clip rows are visible before anything is clicked (computed display %r)"
                         % got.get("row_display_before"))
        if got.get("row_open") != "true":
            fails.append("clip button did not open the clip row")
        if got.get("row_display_after") == "none":
            fails.append("clip row is still not displayed after its button was clicked")
        if "after the start" not in got.get("err_order", ""):
            fails.append("end-before-start was accepted: %r" % got.get("err_order"))
        if got.get("err_ok", "x") != "":
            fails.append("a valid clip was refused: %r" % got.get("err_ok"))
        # the dash between the times is an en dash; the console decode of the dump does
        # not reliably preserve it, so match the two times around it
        if not re.match(r"^Clip 1:20.2:05$", got.get("btn", "")):
            fails.append("clip button label wrong: %r" % got.get("btn"))
        if got.get("btn_set") != "true":
            fails.append("clip button not marked set")
        if not amp(got.get("watch")).endswith("&t=80"):
            fails.append("watch link does not carry the start time: %r" % got.get("watch"))
        if got.get("clear_shown") != "true":
            fails.append("Clear did not appear once a clip was set")
        if "minutes:seconds" not in got.get("err_text", ""):
            fails.append("a non-time was accepted: %r" % got.get("err_text"))
        if not amp(got.get("iframe")).endswith("?rel=0&autoplay=1&start=80&end=125"):
            fails.append("player iframe does not carry the clip: %r" % got.get("iframe"))
        if v and not amp(got.get("iframe")).startswith(v["embed_url"]):
            fails.append("player iframe is not this video's nocookie embed")
        if got.get("btn_after_clear") != "Set a clip":
            fails.append("Clear did not reset the clip button: %r" % got.get("btn_after_clear"))
        if v and amp(got.get("watch_after_clear")) != v["url"]:
            fails.append("Clear did not reset the watch link: %r" % got.get("watch_after_clear"))
        if not amp(got.get("iframe_after_clear")).endswith("?rel=0&autoplay=1"):
            fails.append("Clear did not reload the open player without the clip: %r"
                         % got.get("iframe_after_clear"))

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
