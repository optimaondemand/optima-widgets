# Optima Widgets

Cross-course interactive widgets for Optima Academy Online, hosted on GitHub Pages and embedded in Canvas via iframe. Course-specific widgets live in their own `<course>-widgets` repos; this repo is for widgets that serve the homeroom page or multiple courses.

## Widgets

| File | What it does | Lives in |
|------|--------------|----------|
| `study-planner.html` | K–12 study planner: a questionnaire (grade, live vs On-Demand enrollment, courses/goals via paste or .txt upload, available days/times, parent coordination, metacognitive focus questions) that generates a personalized weekly schedule, daily routine, or project plan, downloadable as PDF via print. | Canvas homeroom page; embeddable in any course |
| `course-home-builder.html` | **Teacher-facing.** A form that generates a branded Optima course home page. Teachers fill in course name, term/section/meeting time, their own name and email, weekly announcements, quick-access tiles, module cards, and a Commonplace Corner quote; the widget outputs paste-ready HTML with a live preview, a **Copy HTML** button, and a `.html` download. | Not embedded in a course — teachers open it directly and paste the output into a Canvas page |
| `optima-literature/ela-reference-library.html` | **Teacher-facing.** The ELA Reference Library: 226 titles with edition, translator, rights, first-publication and genre data, cover art, search, sort, a taught filter, a printable "my list" checkout card, and data-quality checks behind the ⚙ button. Generated — never hand-edit the HTML. | Not embedded in a course — teachers open it directly |

### optima-literature notes

- The widget is **generated**: run `python _build/build_reference_library.py` from `optima-literature/`.
  It rewrites `ela-reference-library.html` and runs the quality gate. Never hand-edit the HTML.
- `library.json` is the contract between the content pipeline and the presentation layer. Both this
  library and the student Independent Reading library are generated from it, so the two can never
  disagree about a title's rights, edition, or shelf.
- The working copy lives at `OneDrive - OptimaEd\Claude's Playground\Widgets\optima-literature`,
  which is where the build kit reads its sources from. This repo holds a copy — rebuild there, then
  sync here.
- `.gitattributes` exempts the generated HTML and JSON from line-ending conversion so a Windows build
  byte-matches a Linux one. Verify with `git check-attr`, never by reading the file.
- See `optima-literature/HANDOFF.md` for the 2026-08-24 brand redesign notes.

### course-home-builder notes

- Output matches the `course-home.html` reference template: every style is inline, since Canvas strips `<style>` blocks.
- All non-ASCII characters (emoji, curly quotes, en/em dashes) are emitted as numeric character references, so the paste survives Canvas's encoding handling.
- The Tech Help tile ships pre-filled with the Optima tech support Teams meeting link and `target="_blank"`. If that meeting link ever changes, update `TEAMS_TECH_HELP` near the top of the script block.
- Tile and module link fields expect a full Canvas URL — teachers open the destination in Canvas and copy the address bar.
- Work in progress persists in `localStorage`, so a teacher can close the tab and come back to the same form.
- Because this widget is a teacher tool rather than a student activity, it isn't iframed into a course page. Link teachers to the GitHub Pages URL, or hand them the file.

## Embedding in Canvas

Canvas strips `<script>` tags, so widgets are embedded as iframes pointing at GitHub Pages:

```html
<div style="margin: 30px 0; border: 2px solid #2e86c1; border-radius: 12px; overflow: hidden; background: #f8f9fa;">
  <div style="background: #1a5276; color: #fff; padding: 10px 18px; font-family: Arial, Helvetica, sans-serif; font-weight: bold; font-size: 1.05em;">
    My Study Planner
  </div>
  <iframe src="https://optimaondemand.github.io/optima-widgets/study-planner.html" width="100%" height="900" style="border: none; display: block;" allowfullscreen></iframe>
  <div style="padding: 6px 18px; font-family: Arial, sans-serif; font-size: 0.8em; color: #666; background: #eaf2f8;">
    If the planner doesn't load, <a href="https://optimaondemand.github.io/optima-widgets/study-planner.html" target="_blank" rel="noopener">open it in a new tab</a>.
  </div>
</div>
```

The planner is taller than most widgets (it's a multi-step wizard producing a full plan) — 900px height is a good starting point.

## Notes

- Each widget is one self-contained HTML file: no build step, no CDN, no external fonts.
- PDF export uses the browser print dialog (students choose "Save as PDF"); the plan view carries its own print stylesheet.
- Student answers persist in `localStorage`, so a page reload doesn't lose progress.
- Updating a widget: edit, commit, push — GitHub Pages redeploys in ~60 seconds and Canvas picks it up on next load. Don't rename files; the filename is in every embed URL.
