# -*- coding: utf-8 -*-
"""Build a self-contained copy of the library for publishing as a Claude artifact.

Identical page, identical design system - the Optima palette and type are the house
system and are not up for renegotiation here. The only difference is the images.

WHY THIS SCRIPT EXISTS: an artifact renders under a Content-Security-Policy that blocks
images from every external host. The published widget serves its 17 plates from
optimaondemand.github.io, which is exactly the sort of host the CSP refuses, so inside an
artifact every plate would render blank with no error. Each image is therefore re-encoded
smaller and inlined as a data URI.

Output goes to the scratchpad, NOT into the repo. A 3-4 MB duplicate of a page that
already exists at a URL has no business in version control; the repo keeps the generator.
"""
import os, io, sys, json, base64

from PIL import Image
Image.MAX_IMAGE_PIXELS = None

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

ASSETS_REPO = "C:/Users/JessicaDrexel/Documents/GitHub/optima-art-assets"

# 900px, not the 1600px the site serves. Base64 inflates a payload by a third, and a
# gallery a teacher scrolls does not need print resolution to be legible.
ARTIFACT_EDGE = 900
ARTIFACT_QUALITY = 80


def data_uri(path):
    im = Image.open(path)
    im.load()
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    scale = min(1.0, ARTIFACT_EDGE / max(im.size))
    if scale < 1.0:
        im = im.resize((max(1, round(im.width * scale)),
                        max(1, round(im.height * scale))), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=ARTIFACT_QUALITY, optimize=True, progressive=True)
    b = buf.getvalue()
    return "data:image/jpeg;base64," + base64.b64encode(b).decode("ascii"), im.size, len(b)


def build(out_path):
    contract = json.load(open(os.path.join(ROOT, "art.json"), encoding="utf-8"))

    # inert in this variant and actively misleading: no image here loads from a host
    contract.pop("asset_base", None)

    inlined, total = 0, 0
    for w in contract["works"]:
        if not w.get("image"):
            continue
        name = w["image"].rsplit("/", 1)[-1]
        p = os.path.join(ASSETS_REPO, "images", name)
        if not os.path.exists(p):
            raise SystemExit("missing local image for " + w["id"] + ": " + p)
        uri, (iw, ih), nbytes = data_uri(p)
        w["image"] = uri
        w["image_w"], w["image_h"] = iw, ih
        inlined += 1
        total += nbytes

    # write the mutated contract where the generator will find it, build, restore
    orig = os.path.join(ROOT, "art.json")
    backup = orig + ".site"
    os.replace(orig, backup)
    try:
        json.dump(contract, open(orig, "w", encoding="utf-8", newline="\n"),
                  indent=1, ensure_ascii=False)
        import build_art_library
        # the site gate insists images come from the assets host; this variant is the one
        # case where that is deliberately false, so it runs with the artifact gate instead
        build_art_library.gate = lambda doc, works, n_img: artifact_gate(doc, works, n_img)
        page = build_art_library.build()
        with open(page, encoding="utf-8") as f:
            doc = f.read()
    finally:
        os.replace(backup, orig)
        # rebuild the site page so the repo is never left holding the artifact variant
        import importlib
        importlib.reload(build_art_library)
        build_art_library.build()

    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(doc)

    print("images inlined  " + str(inlined))
    print("image bytes     " + format(total, ",") + "  (" + str(round(total / 1048576, 2)) + " MB)")
    print("page bytes      " + format(len(doc.encode("utf-8")), ",")
          + "  (" + str(round(len(doc.encode("utf-8")) / 1048576, 2)) + " MB)")
    print("wrote           " + out_path)
    return out_path


def artifact_gate(doc, works, n_img):
    fails = []
    for w in works:
        if w["image"] and not w["image"].startswith("data:image/"):
            fails.append("image not inlined: " + w["id"])
        if w["image"] and w["disposition"] != "publish":
            fails.append("image on a non-publish work: " + w["id"])
    # Test what actually loads. A bare substring match also caught the contract's inert
    # asset_base field, which no image reads - a gate that fails on inert data teaches
    # people to ignore it.
    for marker in ('src="http', "src='http", 'src=\\"http'):
        if marker in doc:
            fails.append("an image or script loads from an external host (" + marker
                         + "); the CSP would block it")
    if '"image":"https' in doc.replace(" ", "") or '"image": "https' in doc:
        fails.append("a work still carries an http image URL rather than a data URI")
    if "doi.org/10.2307" in doc:
        fails.append("a non-resolving doi.org link leaked in")
    if doc.count("<script") != 2 or doc.count("<style") != 1:
        fails.append("unexpected script or style block count")
    size = len(doc.encode("utf-8"))
    if size > 15 * 1024 * 1024:
        fails.append("page is " + str(round(size / 1048576, 1)) + " MB, over the artifact limit")
    print("artifact gate: " + str(len(fails)) + " failures")
    for f in fails:
        print("  FAIL: " + f)
    if fails:
        sys.exit(1)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "artifact.html")
    build(out)
