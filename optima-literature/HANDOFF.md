# optima-literature — brand redesign handoff

**From:** Jorge Acevedo (with Claude) · **Date:** 2026-08-24
**Replaces:** the previous contents of `Claude's Playground/Widgets/optima-literature`
**Approved by:** Jessica Drexel

## What this is

The teacher-facing ELA Reference Library, redesigned to the Optima brand
guidelines v2.0 (July 2026). Same data, same pipeline, same quality gate —
only the presentation and the agreed structural changes are different.
`ela-reference-library.html` is ready to deploy as-is; all 226 records were
verified field-by-field identical to the previous build.

## What changed

**Design**
- Optima brand palette: Binary Blue `#0E1C42` chrome, Bitstream Blue `#55C8E8`
  accent; badges use the guide's darkened variants (Free `#4B7F20`,
  Similar `#0E5568`, Buy / ★ Taught `#B85F00`, warnings `#8F347F`) so every
  badge clears 4.5:1 contrast. Cream retired for a light blue-tinted ground.
- Wix Madefor Display / Text (the brand faces) from Google Fonts, with system
  fallbacks so Canvas iframes and offline viewing still look right.
  **The sans-serif-only house rule is intact** — the gate still enforces it.
- Cover art on every card with an ISBN, from `covers.openlibrary.org`
  (same source as the edition data). Lazy-loaded; on a miss the `onerror`
  hides the image and a genre-coloured spine placeholder shows instead, so
  nothing ever looks broken. Cards also carry a genre-coloured spine edge.
- "My list" is styled as a library pocket card: date stamp, Teacher/Class
  blanks to fill in by hand, stamped section labels, ruled lines. Prints on
  white to save ink; the card structure survives because it is borders and
  text, not background colour.

**Structure (per Jessica's 2026-08-21 feedback, scoped with Jorge)**
- Stat counters removed from the hero.
- Author dropdown removed (search still matches authors; "By author" sort stays).
- "Translations" view removed — the Archaic/Older flags still render on every
  card and in the key.
- "Three lists" and "Needs attention" are intact but live behind the
  "⚙ Data checks" button in the tab bar, so teachers see three tabs.
- The taught filter ("Listed and taught") was kept.

**Pipeline**
- `_build/genre_snapshot.json` (new): a frozen copy of the genre harvest.
  `genres.py` uses it only when `reading_bank_data.py` is not on the machine,
  so rebuilds on other computers no longer silently unshelve 112 titles.
  On Jessica's machine the live harvest still wins.
- The gate now also requires the new elements (viewbar gear, cover
  placeholders, checkout-card header, brand fonts) and **fails the build if a
  removed element reappears** (stat counters, author dropdown, Translations
  view) — protection against old code getting merged back.

## How to rebuild

Unchanged: `python _build/build_reference_library.py` from the widget root
writes `ela-reference-library.html`. Never hand-edit the HTML.

## Still open (not in this drop)

- Student-facing library restyle to match this design.
- Real OAO logo asset (the hero currently uses the owl PNG from the
  optima-assets repo, and hides itself gracefully if unreachable).
- Ideas parked with Jorge: hero bookshelf strip, student book reviews with
  teacher approval. Serif titles would need the sans-serif gate rule lifted.
