# Optima Widgets

Cross-course interactive widgets for Optima Academy Online, hosted on GitHub Pages and embedded in Canvas via iframe. Course-specific widgets live in their own `<course>-widgets` repos; this repo is for widgets that serve the homeroom page or multiple courses.

## Widgets

| File | What it does | Lives in |
|------|--------------|----------|
| `study-planner.html` | K–12 study planner: a questionnaire (grade, live vs On-Demand enrollment, courses/goals via paste or .txt upload, available days/times, parent coordination, metacognitive focus questions) that generates a personalized weekly schedule, daily routine, or project plan, downloadable as PDF via print. | Canvas homeroom page; embeddable in any course |

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
