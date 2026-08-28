# -*- coding: utf-8 -*-
"""Generate art-reference-library.html from art.json.

Run from optima-art/:   python _build/build_art_library.py

art.json is the contract, written by _build/build_contract.py in the PRIVATE
optima-art-library repo. This generator never invents a fact and never adjudicates
rights; if a work has no image here it is because the contract says so.

NEVER HAND-EDIT THE HTML. It is overwritten on every run, and a hand-edit would also
bypass the gate at the bottom of this file.
"""
import os, sys, json, html, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from art_library_css import CSS
from art_library_js import JS

# Reuse the official wordmark already embedded for the ELA Reference Library rather than
# carrying a second copy of the same base64. Both pages sit in this repo.
LOGO_SRC = os.path.join(os.path.dirname(ROOT), "optima-literature", "_build", "brand_assets.py")


def load_logo():
    ns = {}
    with open(LOGO_SRC, encoding="utf-8") as f:
        exec(compile(f.read(), LOGO_SRC, "exec"), ns)
    return ns["OAO_LOGO"]


def e(s):
    return html.escape("" if s is None else str(s), quote=True)


def options(label_all, values):
    out = ['<option value="">' + e(label_all) + "</option>"]
    for v, n in values:
        out.append('<option value="' + e(v) + '">' + e(v) + " (" + str(n) + ")</option>")
    return "".join(out)


def build():
    contract = json.load(open(os.path.join(ROOT, "art.json"), encoding="utf-8"))
    works = contract["works"]
    counts = contract["counts"]

    n_img = sum(1 for w in works if w["image"])
    n_link = sum(1 for w in works if w["jstor_url"])
    n_neither = sum(1 for w in works if not w["image"] and not w["jstor_url"])

    courses = collections.Counter(c for w in works for c in w["courses"])
    movements = collections.Counter(
        t["label"] for w in works for t in w["tags"] if t["scheme"] == "art.movement")

    parts = []
    A = parts.append
    A("<!doctype html>")
    A('<html lang="en"><head><meta charset="utf-8">')
    A('<meta name="viewport" content="width=device-width,initial-scale=1">')
    A("<title>Optima Art Reference Library</title>")
    A('<meta name="description" content="Searchable catalogue of the artwork used across '
      'Optima art courses, with rights status and image availability for each work.">')
    A("<style>" + CSS + "</style>")
    A("</head><body>")

    # ---------------- hero ----------------
    A('<header class="hero"><div class="wrap">')
    A('<div class="brandrow"><img src="' + load_logo() + '" alt="Optima Academy Online">')
    A('<div class="rule"></div><h1>Art Reference Library</h1></div>')
    A('<p class="sub">Every artwork used across the Optima art courses, catalogued once. '
      'Search by artist, title, period, course or subject. Each record states whether the '
      'image may be used and where to view it if not.</p>')
    A('<div class="statline">')
    A('<div class="stat"><b>' + str(len(works)) + "</b><span>Works catalogued</span></div>")
    A('<div class="stat hasimg"><b>' + str(n_img) + "</b><span>Images published</span></div>")
    A('<div class="stat linkonly"><b>' + str(n_link) + "</b><span>Viewable on JSTOR</span></div>")
    A('<div class="stat"><b>' + str(len(courses)) + "</b><span>Courses drawn from</span></div>")
    A("</div></div></header>")

    # ---------------- controls ----------------
    A('<section class="controls"><div class="wrap">')
    A('<div class="searchrow">')
    A('<div class="searchbox"><span class="mag">&#9906;</span>')
    A('<input id="q" type="search" autocomplete="off" placeholder="Search artist, title, '
      'period, course&hellip;" aria-label="Search the catalogue"></div>')
    A('<select id="course" aria-label="Filter by course">'
      + options("All courses", courses.most_common()) + "</select>")
    A('<select id="movement" aria-label="Filter by period or movement">'
      + options("All periods", sorted(movements.items())) + "</select>")
    A('<select id="sort" aria-label="Sort">'
      '<option value="default">Images first</option>'
      '<option value="artist">Artist A&ndash;Z</option>'
      '<option value="title">Title A&ndash;Z</option>'
      '<option value="oldest">Oldest first</option>'
      '<option value="newest">Newest first</option></select>')
    A('<button class="gearbtn" id="gear" type="button" '
      'aria-label="Rights and data notes">&#9881; Rights &amp; data</button>')
    A("</div>")
    A('<div class="chips">')
    A('<button class="chip" type="button" data-avail="image" aria-pressed="false">'
      'Image available<span class="n">' + str(n_img) + "</span></button>")
    A('<button class="chip gold" type="button" data-avail="link" aria-pressed="false">'
      'JSTOR link only<span class="n">' + str(n_link - n_img) + "</span></button>")
    A('<button class="chip" type="button" data-avail="neither" aria-pressed="false">'
      'No image, no link<span class="n">' + str(n_neither) + "</span></button>")
    A("</div>")
    A('<p class="resultline" id="resultline"></p>')
    A("</div></section>")

    # ---------------- standing notice + panel ----------------
    A('<div class="wrap">')
    A('<div class="notice"><b>Most of this catalogue is link-only, and that is a licence '
      'question rather than a copyright one.</b> The source files were exported from '
      'Artstor (now Images on JSTOR) and carry an embedded licence forbidding '
      'redistribution. A painting can be centuries out of copyright and still not ours to '
      'republish. Those works are catalogued with a JSTOR link, which needs an Optima '
      'login. Works are progressively re-sourced from Wikimedia Commons and museum '
      'open-access programmes.</div>')

    A('<section class="panel" id="panel">')
    A("<h2>Rights and data notes</h2>")
    A("<h3>What may be done with each work</h3>")
    A("<table><thead><tr><th>Status</th><th>Works</th><th>What it means</th></tr></thead><tbody>")
    for key, label, meaning in (
        ("publish", "Image available",
         "The file itself carries an explicit CC0 public-domain dedication. Use the image freely."),
        ("re-source", "Public domain, no free copy yet",
         "The artwork is out of copyright but our copy is not redistributable. A freely "
         "licensed copy needs to be found before the image can be published."),
        ("link-only", "JSTOR only",
         "Still in copyright, or the photograph carries its own copyright even though the "
         "subject does not. Link out; never reproduce."),
        ("research", "Date unconfirmed",
         "No reliable date established, so no rights call can be made. Held deliberately "
         "rather than guessed.")):
        A("<tr><td>" + e(label) + '</td><td class="num">' + str(counts.get(key, 0))
          + "</td><td>" + e(meaning) + "</td></tr>")
    A("</tbody></table>")

    A("<h3>How a rights call is made</h3>")
    A("<p>Three tests, all of which must pass before an image is published. <b>The "
      "artwork</b> must be out of copyright. <b>The photograph</b> must add no new "
      "copyright of its own, which a flat reproduction of a flat painting does not but a "
      "photograph of a sculpture, a building or a cave wall does. <b>The licence our copy "
      "arrived under</b> must permit redistribution. A date check alone gets the second "
      "and third wrong, so it is never used alone.</p>")
    A("<p>Dates and attributions come from each image file's own embedded metadata where "
      "it exists, not from its filename. Filenames recorded what a course believed and "
      "were wrong often enough to be untrustworthy: one attributed the Narmer Palette to "
      "the Safavid period. " + str(sum(1 for w in works if w["sourced"]))
      + " of " + str(len(works)) + " records now carry file-sourced identity.</p>")

    A("<h3>Cross-subject tagging</h3>")
    A("<p>Tags are an open list rather than fixed columns, so a new subject is a new "
      "scheme value and never a rebuild. Present today: "
      + e(", ".join(sorted(contract["tag_schemes"]["present"]))) + ". Reserved for the "
      "interdisciplinary layer: <code>concept</code>, so a maths or ELA teacher can find "
      "art by idea rather than by period, and <code>standard</code> for jurisdiction "
      "standard codes. Neither is populated yet.</p>")

    A("<h3>Provenance</h3>")
    A("<p>" + e(contract["provenance_note"]) + "</p>")
    A("<p>Generated " + e(contract["generated"]) + " from art.json. This page is built by "
      "<code>_build/build_art_library.py</code> and is overwritten on every run; edit the "
      "generator, never the HTML.</p>")
    A("</section>")
    A("</div>")

    # ---------------- grid ----------------
    A('<main class="wrap"><div class="grid" id="grid"></div></main>')
    A('<footer class="wrap">Optima Academy Online &middot; Art Reference Library &middot; '
      "teacher reference. Rights statuses are a documented screen, not legal advice; when "
      "a use matters, check the source record.</footer>")

    A("<script>var ART=" + json.dumps(contract, ensure_ascii=False, separators=(",", ":"))
      + ";</script>")
    A("<script>" + JS + "</script>")
    A("</body></html>")

    doc = "\n".join(parts)
    out = os.path.join(ROOT, "art-reference-library.html")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(doc)

    gate(doc, works, n_img)
    print("wrote " + out)
    print("  " + format(len(doc.encode("utf-8")), ",") + " bytes"
          + "  |  " + str(len(works)) + " works, " + str(n_img) + " images")
    return out


def gate(doc, works, n_img):
    """Fail the build rather than ship a page that misstates rights."""
    fails = []

    def check(cond, msg):
        if not cond:
            fails.append(msg)

    check(doc.count("<html") == 1 and doc.rstrip().endswith("</html>"), "malformed document")
    check(doc.count("<style") == 1, "expected exactly one style block")
    check(doc.count("<script") == 2, "expected exactly two script blocks")
    check("preview-banner" not in doc, "a preview banner leaked into the page")
    check("facilitator" not in doc.lower(), "the word facilitator appears; say teacher")

    # every published image must point at the assets host, never at a museum or a local path
    for w in works:
        if w["image"] and not w["image"].startswith(
                "https://optimaondemand.github.io/optima-art-assets/"):
            fails.append("image not served from the assets repo: " + w["id"])
    # and nothing without a publish disposition may carry an image
    for w in works:
        if w["image"] and w["disposition"] != "publish":
            fails.append("image on a non-publish work: " + w["id"])
        if w["disposition"] == "publish" and not w["image"]:
            fails.append("publish disposition with no image: " + w["id"])
    # a held work must tell the teacher why
    for w in works:
        if w["disposition"] != "publish" and not w["why"]:
            fails.append("held work with no reason given: " + w["id"])

    check(n_img > 0, "no images at all: the contract was probably built without a manifest")
    check("jstor.org/stable/" in doc, "no JSTOR links in the page")
    # doi.org 404s on Artstor community ids; the resolving form is the stable path
    check("doi.org/10.2307" not in doc, "a non-resolving doi.org link leaked in")

    print("gate: " + str(len(fails)) + " failures")
    for f in fails:
        print("  FAIL: " + f)
    if fails:
        sys.exit(1)


if __name__ == "__main__":
    build()
