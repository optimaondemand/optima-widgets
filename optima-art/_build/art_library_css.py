# -*- coding: utf-8 -*-
"""Presentation layer for the Art Reference Library.

Two accents on navy and nothing else: cyan for structure and interaction, gold for the
one thing a teacher must not miss, that most of this catalogue is link-only. Green and
red appear only functionally, never decoratively.

Sans-serif throughout. The library feel is carried by layout, colour and the plate-style
image frames rather than by a serif face.
"""

CSS = """
:root{
  --navy:#0f2340; --navy-2:#17325c; --navy-3:#1f4275;
  --cyan:#31c3d6; --cyan-dim:#1c7f8d;
  --gold:#e0aa3e; --gold-dim:#8a6a25;
  --ink:#12202f; --body:#3d4b5c; --mute:#6b7a8d;
  --page:#f4f6f9; --card:#ffffff; --line:#dde3ec;
  --ok:#2e7d55; --warn:#8a4b12;
  --sans:"Segoe UI",system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;
  --shadow:0 1px 2px rgba(15,35,64,.06),0 6px 18px rgba(15,35,64,.07);
}
*{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--body);font-family:var(--sans);
  font-size:16px;line-height:1.55;-webkit-font-smoothing:antialiased}
.wrap{max-width:1280px;margin:0 auto;padding:0 24px}

/* ---------- hero ---------- */
.hero{background:linear-gradient(135deg,var(--navy) 0%,var(--navy-3) 100%);color:#fff;
  padding:34px 0 30px;border-bottom:3px solid var(--cyan)}
.hero .wrap{display:flex;flex-direction:column;gap:16px}
.brandrow{display:flex;align-items:center;gap:18px;flex-wrap:wrap}
.brandrow img{height:44px;width:auto;display:block}
.brandrow .rule{width:1px;height:40px;background:rgba(255,255,255,.28)}
h1{margin:0;font-size:26px;font-weight:650;letter-spacing:-.2px;color:#fff}
.sub{margin:0;color:#c3d3e8;font-size:15px;max-width:70ch}
.statline{display:flex;gap:26px;flex-wrap:wrap;margin-top:4px}
.stat{display:flex;flex-direction:column}
.stat b{font-size:23px;font-weight:680;color:#fff;line-height:1.15}
.stat span{font-size:12px;text-transform:uppercase;letter-spacing:.09em;color:#9fb6d4}
.stat.hasimg b{color:var(--cyan)}
.stat.linkonly b{color:var(--gold)}

/* ---------- controls ---------- */
.controls{position:sticky;top:0;z-index:20;background:rgba(244,246,249,.96);
  backdrop-filter:blur(8px);border-bottom:1px solid var(--line);padding:14px 0}
.searchrow{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
.searchbox{flex:1 1 300px;position:relative;min-width:240px}
.searchbox input{width:100%;padding:11px 14px 11px 38px;font:inherit;color:var(--ink);
  background:#fff;border:1px solid var(--line);border-radius:8px;outline:none}
.searchbox input:focus{border-color:var(--cyan);box-shadow:0 0 0 3px rgba(49,195,214,.18)}
.searchbox .mag{position:absolute;left:13px;top:50%;transform:translateY(-50%);
  color:var(--mute);font-size:15px;pointer-events:none}
select{padding:10px 12px;font:inherit;color:var(--ink);background:#fff;
  border:1px solid var(--line);border-radius:8px;outline:none;max-width:230px}
select:focus{border-color:var(--cyan)}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:11px}
.chip{padding:6px 13px;font-size:13.5px;font-weight:550;color:var(--navy-2);background:#fff;
  border:1px solid var(--line);border-radius:999px;cursor:pointer;user-select:none;
  transition:background .12s,border-color .12s,color .12s}
.chip:hover{border-color:var(--cyan-dim)}
.chip[aria-pressed="true"]{background:var(--navy);border-color:var(--navy);color:#fff}
.chip[aria-pressed="true"].gold{background:var(--gold-dim);border-color:var(--gold-dim)}
.chip .n{opacity:.62;font-weight:500;margin-left:5px}
.resultline{margin:13px 0 0;font-size:14px;color:var(--mute)}
.resultline b{color:var(--ink)}
.gearbtn{margin-left:auto;background:none;border:1px solid var(--line);border-radius:8px;
  padding:9px 12px;cursor:pointer;color:var(--body);font:inherit}
.gearbtn:hover{border-color:var(--cyan-dim);color:var(--navy)}

/* ---------- grid ---------- */
.grid{display:grid;gap:20px;padding:24px 0 60px;
  grid-template-columns:repeat(auto-fill,minmax(268px,1fr))}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;
  overflow:hidden;box-shadow:var(--shadow);display:flex;flex-direction:column}
/* Fixed plate height, image contained inside it. Without this each card sizes to its
   own image and the badges and titles in a row start at different heights, which reads
   as a mistake rather than as a gallery. */
.plate{background:#e9edf3;display:flex;align-items:center;justify-content:center;
  padding:16px;height:230px}
.plate img{max-width:100%;max-height:100%;width:auto;height:auto;display:block;
  object-fit:contain;
  box-shadow:0 1px 3px rgba(15,35,64,.22),0 8px 22px rgba(15,35,64,.16)}
.noplate{min-height:96px;display:flex;align-items:center;justify-content:center;
  background:repeating-linear-gradient(135deg,#eef1f6,#eef1f6 9px,#e7ebf2 9px,#e7ebf2 18px);
  color:var(--mute);font-size:12.5px;letter-spacing:.06em;text-transform:uppercase}
.body{padding:14px 15px 15px;display:flex;flex-direction:column;gap:7px;flex:1}
.t{margin:0;font-size:15.5px;font-weight:640;color:var(--ink);line-height:1.32}
.c{margin:0;font-size:14px;color:var(--body)}
.c em{font-style:normal;color:var(--mute)}
.d{margin:0;font-size:13px;color:var(--mute)}
.badge{display:inline-flex;align-items:center;gap:6px;align-self:flex-start;
  padding:3px 9px;border-radius:5px;font-size:11.5px;font-weight:650;
  text-transform:uppercase;letter-spacing:.05em}
.badge.pub{background:#e4f4ec;color:var(--ok)}
.badge.link{background:#fbf1dc;color:var(--warn)}
.badge.res{background:#eef1f6;color:var(--mute)}
.why{margin:0;font-size:12.5px;color:var(--mute);line-height:1.45}
.foot{margin-top:auto;padding-top:11px;border-top:1px solid var(--line);
  display:flex;gap:9px;align-items:center;flex-wrap:wrap}
.jstor{font-size:13px;font-weight:600;color:var(--navy-2);text-decoration:none;
  border:1px solid var(--line);border-radius:7px;padding:6px 11px;background:#fff}
.jstor:hover{border-color:var(--cyan);color:var(--navy)}
.uses{font-size:12px;color:var(--mute)}
.copybtn{font:inherit;font-size:12.5px;font-weight:600;color:var(--navy-2);cursor:pointer;
  background:#fff;border:1px solid var(--line);border-radius:7px;padding:6px 10px}
.copybtn:hover{border-color:var(--cyan)}
.copybtn.done{background:#e4f4ec;border-color:var(--ok);color:var(--ok)}
.empty{padding:70px 20px;text-align:center;color:var(--mute)}
.empty b{display:block;font-size:18px;color:var(--ink);margin-bottom:7px}

/* ---------- notice + panel ---------- */
.notice{margin:20px 0 0;padding:14px 17px;background:#fdf6e6;
  border:1px solid #ecd9a8;border-left:4px solid var(--gold);border-radius:8px;
  font-size:14px;color:#5c4718}
.notice b{color:#3f3010}
.panel{display:none;margin:18px 0 0;padding:20px 22px;background:#fff;
  border:1px solid var(--line);border-radius:12px;box-shadow:var(--shadow)}
.panel.open{display:block}
.panel h2{margin:0 0 12px;font-size:17px;color:var(--ink)}
.panel h3{margin:20px 0 8px;font-size:14px;text-transform:uppercase;
  letter-spacing:.07em;color:var(--mute)}
.panel table{border-collapse:collapse;width:100%;font-size:14px}
.panel th,.panel td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--line)}
.panel th{color:var(--mute);font-weight:600;font-size:12.5px;text-transform:uppercase;
  letter-spacing:.05em}
.panel td.num{text-align:right;font-variant-numeric:tabular-nums;font-weight:600;
  color:var(--ink)}
.panel p{font-size:14px}
.panel code{background:#eef1f6;padding:1.5px 5px;border-radius:4px;font-size:13px}
footer{padding:26px 0 40px;color:var(--mute);font-size:13px;border-top:1px solid var(--line)}

/* ---------- subject chips ---------- */
.subjects{display:flex;gap:8px;flex-wrap:wrap;margin-top:11px;
  padding-top:11px;border-top:1px dashed var(--line)}
.subjects .lab{font-size:12px;text-transform:uppercase;letter-spacing:.08em;
  color:var(--mute);align-self:center;margin-right:2px}
.subj{padding:5px 11px;font-size:13px;font-weight:550;color:var(--navy-2);background:#fff;
  border:1px solid var(--line);border-radius:6px;cursor:pointer}
.subj:hover{border-color:var(--cyan-dim)}
.subj[aria-pressed="true"]{background:var(--cyan-dim);border-color:var(--cyan-dim);color:#fff}
.subj .n{opacity:.62;font-weight:500;margin-left:5px}
.conceptnote{margin:9px 0 0;font-size:13px;color:var(--mute);max-width:78ch}
.conceptnote b{color:var(--ink)}

/* ---------- concept pills on a card ---------- */
.cpills{display:flex;gap:5px;flex-wrap:wrap}
.cpill{font-size:11px;font-weight:600;letter-spacing:.02em;padding:2px 7px;border-radius:4px;
  background:#e7f6f8;color:var(--cyan-dim);border:1px solid #c8e9ee;cursor:help}

/* ---------- lesson bundle tray ---------- */
.addbtn{font:inherit;font-size:12.5px;font-weight:600;color:var(--navy-2);cursor:pointer;
  background:#fff;border:1px solid var(--line);border-radius:7px;padding:6px 10px}
.addbtn:hover{border-color:var(--cyan)}
.addbtn.in{background:var(--navy);border-color:var(--navy);color:#fff}
.tray{position:fixed;left:0;right:0;bottom:0;z-index:40;background:var(--navy);
  color:#fff;box-shadow:0 -3px 18px rgba(15,35,64,.28);transform:translateY(100%);
  transition:transform .18s ease}
.tray.open{transform:translateY(0)}
.tray .wrap{display:flex;align-items:center;gap:16px;padding:13px 24px;flex-wrap:wrap}
.tray .count{font-size:15px;font-weight:650}
.tray .count span{color:var(--cyan)}
.tray .names{flex:1;min-width:180px;font-size:13px;color:#b9cbe4;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tray button{font:inherit;font-size:13.5px;font-weight:600;cursor:pointer;
  border-radius:7px;padding:8px 14px;border:1px solid rgba(255,255,255,.34);
  background:transparent;color:#fff}
.tray button.primary{background:var(--cyan);border-color:var(--cyan);color:#08222e}
.tray button:hover{border-color:#fff}
.tray button.primary:hover{background:#48d3e5}
body.hastray{padding-bottom:74px}

@media (prefers-reduced-motion:reduce){
  .tray{transition:none}
}

@media (max-width:640px){
  .wrap{padding:0 16px}
  h1{font-size:22px}
  .grid{grid-template-columns:1fr;gap:16px}
  .statline{gap:18px}
  select{max-width:100%;flex:1 1 140px}
  .tray .wrap{padding:11px 16px;gap:10px}
  .tray .names{display:none}
}
"""
