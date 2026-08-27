# -*- coding: utf-8 -*-
"""
reference_library_assets.py — CSS and JS for the ELA Reference Library.

Kept separate from the generator so the Python stays readable.

Tokens follow the Optima brand guidelines v2.0 (July 2026): Binary Blue
#0E1C42 anchor, Bitstream Blue #55C8E8 accent, and the guide's darkened
accent variants for text and badges so everything clears 4.5:1 contrast
(Dark Gamer Green #4B7F20 = free, Dark Bitstream Blue #0E5568 = similar,
Dark Odyssey Orange #B85F00 = buy/taught, Dark Portal Purple #8F347F =
warnings). Type is Wix Madefor Display / Text, the brand faces, loaded from
Google Fonts with system fallbacks. This page sets the new house style; the
student Independent Reading library is to be restyled to match it, not the
other way around (decided with Jorge, 2026-08-24).

NOTE: only CSS below is consumed by build_reference_library.py. The JS
constant at the bottom is the pre-views legacy behaviour, superseded by
reference_library_js.py; it is kept for reference only.
"""

CSS = """
:root{
  --navy:#0E1C42;          /* Binary Blue — brand primary */
  --accent:#55C8E8;        /* Bitstream Blue — brand primary */
  --accent-ink:#0E5568;    /* Dark Bitstream Blue — accent as text */
  --free:#4B7F20;          /* Dark Gamer Green */
  --sim:#0E5568;           /* Dark Bitstream Blue */
  --buy:#B85F00;           /* Dark Odyssey Orange */
  --warn:#8F347F;          /* Dark Portal Purple */
  --ink:#131A2C; --ink-soft:#51617C; --ink-faint:#8DA0B6;
  --ground:#F4F8FB; --card:#FFFFFF; --line:#DCE6EF; --line-soft:#EAF1F7;
  --note-bg:#EAF6FB;
  --display:"Wix Madefor Display","Wix Madefor Text","Segoe UI",Roboto,Arial,sans-serif;
  --body:"Wix Madefor Text","Segoe UI",Roboto,Helvetica,Arial,sans-serif;
}
*{box-sizing:border-box;}
body{margin:0;padding:0;font-family:var(--body);
     background:var(--ground);color:var(--ink);-webkit-font-smoothing:antialiased;}
.sheet{max-width:1240px;margin:0 auto;}
a{color:var(--accent-ink);}

.hero{position:relative;overflow:hidden;background:
      radial-gradient(1200px 340px at 18% -40%, #24406e 0%, rgba(36,64,110,0) 62%),
      linear-gradient(135deg,#0E1C42 0%,#16294E 55%,#0A1631 100%);
      padding:30px 34px 26px 34px;border-bottom:4px solid var(--accent);}
.brandrow{display:flex;align-items:center;gap:16px;}
/* The official OAO wordmark, reversed for the navy hero. Sized in CSS as
   well as on the element, so it cannot jump while the page paints. */
.oaologo{height:46px;width:auto;flex-shrink:0;display:block;}
@media (max-width:820px){ .oaologo{height:36px;} }
@media (max-width:430px){ .oaologo{height:30px;} }

/* .owl is no longer emitted; the wordmark contains the owl. Kept so the
   owl-only mark can be restored without rewriting the stylesheet. */
.owl{width:52px;height:52px;border-radius:50%;background:#fff;display:flex;
     align-items:center;justify-content:center;flex-shrink:0;
     box-shadow:0 0 0 3px rgba(85,200,232,.4);overflow:hidden;}
.owl img{width:40px;height:40px;object-fit:contain;}
.hero h1{margin:0;font-family:var(--display);font-weight:800;font-size:32px;
     color:#fff;letter-spacing:.2px;line-height:1.15;}
.hero h1 .accent{color:var(--accent);}
.hero .sub{font-size:13.5px;color:rgba(255,255,255,.78);margin-top:7px;
           max-width:700px;line-height:1.6;}

.key{margin:22px 34px;background:var(--card);border:1px solid var(--line);
     border-left:5px solid var(--accent);border-radius:12px;padding:16px 20px;
     box-shadow:0 1px 3px rgba(14,28,66,.05);}
.key h2{margin:0 0 10px 0;font-family:var(--display);font-size:15px;
     color:var(--navy);letter-spacing:.3px;}
.keyrow{display:flex;flex-wrap:wrap;gap:9px 20px;}
.keyitem{display:flex;align-items:center;gap:8px;font-size:12.5px;line-height:1.5;}
.key .fine{margin:11px 0 0 0;font-size:12px;color:var(--ink-soft);line-height:1.6;}

/* ---------- view menu ---------- */
.viewbar{background:var(--navy);padding:0 34px;border-bottom:3px solid var(--accent);
     position:sticky;top:0;z-index:31;}
.vrow{display:flex;gap:2px;overflow-x:auto;scrollbar-width:thin;align-items:center;}
.vtab{font-family:inherit;font-size:13.5px;padding:13px 17px;border:none;
     background:transparent;color:rgba(255,255,255,.68);cursor:pointer;
     border-bottom:3px solid transparent;white-space:nowrap;transition:.14s;
     letter-spacing:.2px;}
.vtab:hover{color:#fff;background:rgba(255,255,255,.06);}
.vtab[aria-pressed="true"]{color:#fff;border-bottom-color:var(--accent);
     background:rgba(85,200,232,.12);font-weight:600;}
.vtab.admin{display:none;}
.viewbar.show-admin .vtab.admin{display:block;}
.gearbtn{margin-left:auto;font-family:inherit;font-size:15px;padding:13px 10px;
     border:none;background:transparent;color:rgba(255,255,255,.55);
     cursor:pointer;transition:.14s;white-space:nowrap;}
.gearbtn:hover{color:#fff;}
.gearbtn[aria-expanded="true"]{color:var(--accent);}
.sep{width:1px;height:22px;background:var(--line);margin:0 4px;}

/* ---------- table views ---------- */
.views{padding:20px 34px 90px 34px;}
.vhead{margin:0 0 4px 0;font-family:var(--display);color:var(--navy);font-size:20px;}
.vlede{color:var(--ink-soft);font-size:13px;line-height:1.65;margin:0 0 18px 0;max-width:760px;}
.tw{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:var(--card);
     box-shadow:0 1px 3px rgba(14,28,66,.05);}
table.vt{border-collapse:collapse;width:100%;font-size:13px;min-width:640px;}
table.vt th{background:#EDF3F8;color:var(--navy);text-align:left;padding:10px 13px;
     font-size:11px;text-transform:uppercase;letter-spacing:.6px;
     border-bottom:2px solid var(--line);position:sticky;top:0;white-space:nowrap;}
table.vt td{padding:10px 13px;border-bottom:1px solid var(--line-soft);vertical-align:top;
     line-height:1.5;}
table.vt tr:last-child td{border-bottom:none;}
table.vt tr:hover td{background:#F7FAFC;}
table.vt td.t{font-weight:600;color:var(--navy);}
table.vt td.m{color:var(--ink-soft);font-size:12px;}
table.vt td.n{text-align:right;font-variant-numeric:tabular-nums;
     font-feature-settings:"tnum";}
.pill{display:inline-block;font-size:10.5px;text-transform:uppercase;
     letter-spacing:.5px;font-weight:700;color:#fff;background:var(--bc);
     border-radius:5px;padding:2px 7px;white-space:nowrap;}
.diff{background:#FAF2F8;}
.agree{color:var(--free);font-weight:600;}
.clash{color:var(--warn);font-weight:600;}
.vgrp{margin-bottom:30px;}
.bar{display:flex;height:22px;border-radius:5px;overflow:hidden;min-width:130px;
     background:var(--line-soft);}
.bar i{display:block;}
.tick{background:none;border:1.5px solid var(--line);border-radius:6px;
     font-family:inherit;font-size:11px;padding:4px 9px;cursor:pointer;
     color:var(--navy);white-space:nowrap;}
.tick:hover{border-color:var(--accent);background:var(--note-bg);}

.controls{position:sticky;top:48px;z-index:30;background:rgba(255,255,255,.97);
          backdrop-filter:blur(6px);border-bottom:1px solid var(--line);padding:11px 34px;}
.crow{display:flex;flex-wrap:wrap;align-items:center;gap:8px;}
.crow+.crow{margin-top:8px;}
.lbl{font-size:10px;color:var(--ink-soft);letter-spacing:.7px;min-width:46px;
     text-transform:uppercase;}
.tab{font-family:inherit;font-size:13.5px;padding:7px 15px;border-radius:999px;
     cursor:pointer;border:1.5px solid var(--line);background:var(--card);color:var(--navy);
     transition:.15s;}
.tab:hover{border-color:var(--accent-ink);transform:translateY(-1px);}
.tab[aria-pressed="true"]{background:var(--navy);border-color:var(--navy);color:#fff;
     box-shadow:0 3px 10px rgba(14,28,66,.25);}
select,#q{font-family:inherit;font-size:13.5px;padding:8px 11px;
     border:1.5px solid var(--line);border-radius:9px;color:var(--navy);background:var(--card);}
#q{min-width:230px;}
#q:focus,select:focus{outline:none;border-color:var(--accent);
     box-shadow:0 0 0 3px rgba(85,200,232,.25);}
.js-only{display:none;}
.count{font-size:12px;color:var(--ink-soft);margin-left:auto;}

.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));
      gap:16px;padding:22px 34px 90px 34px;}
.secthead{grid-column:1/-1;margin:14px 0 2px 0;padding-bottom:7px;
      border-bottom:2px solid var(--line);font-family:var(--display);
      color:var(--navy);font-size:17px;
      display:flex;align-items:baseline;gap:10px;}
.secthead span{font-size:11.5px;color:var(--ink-soft);font-weight:400;}
.noresult{grid-column:1/-1;padding:40px 0;text-align:center;color:var(--ink-faint);
      font-size:14px;}

.book{position:relative;background:var(--card);border:1px solid var(--line);
      border-left:4px solid var(--sc,var(--line));border-radius:12px;
      padding:16px 17px 14px 15px;box-shadow:0 1px 3px rgba(14,28,66,.05);
      display:flex;flex-direction:column;gap:8px;transition:.15s;}
.book:hover{box-shadow:0 5px 16px rgba(14,28,66,.11);transform:translateY(-2px);}
.book.sel{border-color:var(--accent);border-left-color:var(--sc,var(--accent));
      box-shadow:0 0 0 2px rgba(85,200,232,.45);}

/* Cover art: the Open Library image sits on top of a genre-coloured spine
   placeholder. When the cover 404s (no ISBN match) the img hides itself and
   the placeholder underneath simply shows through. */
.brow{display:flex;gap:13px;align-items:flex-start;}
.bhead{display:flex;flex-direction:column;gap:6px;min-width:0;flex:1;}
.cwrap{position:relative;width:64px;min-width:64px;height:96px;}
.cover-ph{position:absolute;inset:0;border-radius:4px;background:var(--sc,var(--navy));
      background-image:linear-gradient(160deg,rgba(255,255,255,.22),rgba(255,255,255,0) 55%);
      box-shadow:inset 3px 0 0 rgba(0,0,0,.18), 0 2px 6px rgba(14,28,66,.18);
      color:#fff;padding:8px 7px;overflow:hidden;}
.cover-ph span{display:block;font-size:8.5px;font-weight:700;line-height:1.35;
      letter-spacing:.02em;max-height:100%;overflow:hidden;}
.cover{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;
      border-radius:4px;box-shadow:0 2px 6px rgba(14,28,66,.22);}
.bt{font-family:var(--display);font-size:16px;font-weight:700;color:var(--navy);
    line-height:1.3;padding-right:30px;}
.ba{font-size:13px;color:var(--ink-soft);display:flex;gap:7px;flex-wrap:wrap;
    align-items:baseline;}
.yr{color:var(--ink-faint);font-size:11.5px;}
.shelf{font-size:11.5px;color:var(--sc);display:flex;align-items:center;gap:6px;
       letter-spacing:.2px;}
.shelf .gr{margin-left:auto;background:#EAF2F8;color:var(--ink-soft);border-radius:5px;
       padding:1px 8px;font-size:10.5px;font-weight:600;letter-spacing:.4px;}
.pub{font-size:11.5px;color:var(--ink-soft);line-height:1.55;border-top:1px dashed var(--line);
     padding-top:8px;}
.pub.none{color:var(--ink-faint);font-style:italic;}
.course{font-size:11.5px;color:var(--ink);background:var(--note-bg);
     border-left:3px solid var(--accent);
     border-radius:0 6px 6px 0;padding:6px 10px;line-height:1.5;}
.bm{display:flex;flex-wrap:wrap;gap:5px;}
.bdg{font-size:10px;letter-spacing:.6px;text-transform:uppercase;
     font-weight:700;color:#fff;background:var(--bc);border-radius:5px;
     padding:2.5px 8px;cursor:help;}
.acts{display:flex;flex-wrap:wrap;gap:6px;margin-top:2px;}
.act{font-size:11.5px;font-weight:600;text-decoration:none;border-radius:7px;
     padding:5px 11px;border:1.5px solid transparent;transition:.14s;}
.act.buy{border-color:var(--buy);color:var(--buy);}
.act.buy:hover{background:var(--buy);color:#fff;}
.act.free{border-color:var(--free);color:var(--free);}
.act.free:hover{background:var(--free);color:#fff;}
.act.sim{border-color:var(--sim);color:var(--sim);}
.act.sim:hover{background:var(--sim);color:#fff;}
.act.ro{border-color:#67308F;color:#67308F;}
.act.ro:hover{background:#67308F;color:#fff;}

.pick{position:absolute;top:13px;right:13px;cursor:pointer;}
.pick input{position:absolute;opacity:0;width:0;height:0;}
.pick span{position:relative;display:block;width:20px;height:20px;
     border:2px solid var(--line);border-radius:5px;background:var(--card);transition:.14s;}
.pick input:checked+span{background:var(--accent-ink);border-color:var(--accent-ink);}
.pick input:checked+span::after{content:"";position:absolute;left:5px;top:1px;
     width:6px;height:11px;border:solid #fff;border-width:0 2.5px 2.5px 0;
     transform:rotate(45deg);}
.pick input:focus-visible+span{box-shadow:0 0 0 3px rgba(85,200,232,.4);}

.fab{position:fixed;bottom:22px;right:22px;z-index:60;background:var(--navy);
     color:#fff;border:none;border-radius:999px;padding:14px 22px;font-size:14px;
     font-family:inherit;font-weight:600;cursor:pointer;
     box-shadow:0 6px 20px rgba(14,28,66,.32);}
.fab:hover{background:#16294E;}
.fab b{color:var(--accent);}
.panel{position:fixed;inset:0;z-index:70;background:rgba(10,22,49,.55);
     display:none;padding:28px;overflow:auto;}
.panel.open{display:block;}
/* "My list" is styled as a classic library pocket card: buff card stock,
   a ruled header block, a purple ink date stamp, and ruled lines under every
   title. It is the one thing teachers print and send home, so it should feel
   like an object from a library, not a database export. Mono accents use a
   SANS monospace stack — the library's no-serif house rule still holds. */
.sheetbox{max-width:920px;margin:0 auto;background:#FDF9EE;border-radius:6px;
     border:1.5px solid #D9CFB4;
     padding:26px 32px 34px 32px;box-shadow:0 20px 60px rgba(0,0,0,.3);}
.cardhead{border-bottom:3px double #2B3A63;padding-bottom:12px;margin-bottom:4px;
     display:flex;flex-wrap:wrap;align-items:flex-start;gap:4px 16px;}
.ch-left{flex:1;min-width:220px;}
.ch-org{font-size:10.5px;letter-spacing:.22em;text-transform:uppercase;
     color:var(--ink-soft);margin-bottom:3px;}
.ch-title{font-family:var(--display);font-weight:800;font-size:21px;
     color:var(--navy);letter-spacing:.02em;}
.ch-stamp{font-family:ui-monospace,"Cascadia Mono",Consolas,monospace;
     font-size:12px;letter-spacing:.08em;color:#67308F;border:2px solid #67308F;
     border-radius:3px;padding:5px 12px;transform:rotate(1.6deg);opacity:.85;
     align-self:center;white-space:nowrap;}
.ch-meta{font-size:12px;color:var(--ink-soft);letter-spacing:.08em;
     text-transform:uppercase;padding:10px 0 2px 0;border-bottom:1px solid rgba(14,28,66,.25);
     display:flex;gap:14px;flex-wrap:wrap;}
.ch-meta .blank{display:inline-block;min-width:150px;flex:1;
     border-bottom:1px solid rgba(14,28,66,.45);}
.sheetbox h2{margin:0 0 4px 0;font-family:var(--display);color:var(--navy);font-size:22px;}
.sheetbox .lede{color:var(--ink-soft);font-size:13px;margin:10px 0 18px 0;line-height:1.6;}
.grp{margin-bottom:24px;}
.grp h3{display:inline-block;font-size:11.5px;text-transform:uppercase;
     letter-spacing:.14em;color:var(--buy);border:1.5px solid currentColor;
     border-radius:3px;padding:3px 11px;transform:rotate(-.6deg);
     margin:0 0 10px 0;font-family:ui-monospace,"Cascadia Mono",Consolas,monospace;}
.grp.f h3{color:var(--free);}
.grp.s h3{color:var(--sim);}
.li{padding:9px 2px;border-bottom:1px solid rgba(14,28,66,.22);
     font-size:13.5px;line-height:1.6;}
.li b{color:var(--navy);}
.li .m{color:var(--ink-soft);font-size:12px;display:block;}
.li a{font-size:12px;}
.pbtns{display:flex;gap:9px;flex-wrap:wrap;margin-top:6px;}
.pbtn{font-family:inherit;font-size:13px;padding:9px 16px;border-radius:8px;
     cursor:pointer;border:1.5px solid var(--line);background:var(--card);color:var(--navy);}
.pbtn.primary{background:var(--navy);color:#fff;border-color:var(--navy);}
.pbtn:hover{border-color:var(--accent);}
.empty{color:var(--ink-faint);font-style:italic;font-size:13px;}

@media print{
  .hero,.key,.controls,.viewbar,.grid,.views,.fab{display:none !important;}
  .panel{position:static;display:block !important;background:#fff;padding:0;
         overflow:visible;}
  /* Print on white to save ink; the ruled lines, double rule, stamp and
     section labels are borders and text, so the card structure survives. */
  .sheetbox{box-shadow:none;max-width:none;padding:0;background:#fff;border:none;}
  .pbtns{display:none;}
  body{background:#fff;}
}
@media (max-width:640px){
  .hero,.controls{padding-left:18px;padding-right:18px;}
  .viewbar{padding-left:8px;padding-right:8px;}
  .grid{padding-left:18px;padding-right:18px;}
  .key{margin-left:18px;margin-right:18px;}
  #q{min-width:150px;}
}
@media (prefers-reduced-motion: reduce){
  *{transition:none !important;}
}

/* One shelf, on paper. The main @media print block hides .views, so printing a
   shelf means turning that back on for the marked card only. Links print with
   their URL spelled out, because a printed link nobody can type is decoration. */
.tbprintonly{display:none;}
@media print{
  body.tbprinting .views{display:block !important;}
  body.tbprinting .hero,
  body.tbprinting .key,
  body.tbprinting .controls,
  body.tbprinting .viewbar,
  body.tbprinting .grid,
  body.tbprinting .fab,
  body.tbprinting .panel,
  body.tbprinting .vhead,
  body.tbprinting .vlede,
  body.tbprinting .tbstrip,
  body.tbprinting .tbfind{display:none !important;}
  body.tbprinting .views{padding:0;}
  body.tbprinting .tbshelves{display:block !important;}
  body.tbprinting .tbshelf{display:none !important;}
  body.tbprinting .tbshelf.tbprintme{display:block !important;border:none;
       box-shadow:none;border-top:3px solid #0E1C42 !important;}
  body.tbprinting .tbprintme .tbsfoot{display:none !important;}
  body.tbprinting .tbprintme .tbprintonly{display:block !important;
       font-size:11px;color:#333;margin-top:4px;}
  body.tbprinting .tbprintme .tbbk{break-inside:avoid;page-break-inside:avoid;}
  body.tbprinting .tbprintme .tbscount b{color:#000;}
  body.tbprinting .tbprintme .act{border:none;padding:0 6px 0 0;color:#000;
       font-weight:400;}
  /* data-plain, not href: a third of the stored buy URLs are HTML-encoded,
     and a printed URL has to be one a person can actually type. */
  body.tbprinting .tbprintme .act::after{content:" " attr(data-plain);font-size:9px;
       color:#444;word-break:break-all;}
  body.tbprinting{background:#fff;}
}
.tbcopied{border-color:var(--free) !important;color:var(--free) !important;}

/* ---------------- teacher bookshelves ----------------
   My Classroom (the form) and Teacher Bookshelves (the directory). All new
   selectors are tb-prefixed to avoid colliding with .shelf/.empty/.noresult,
   which already mean something else on a book card. */
.tbcard{background:var(--card);border:1px solid var(--line);border-radius:12px;
     box-shadow:0 1px 3px rgba(14,28,66,.05);margin-bottom:18px;overflow:hidden;}
.tbhead{display:flex;align-items:baseline;gap:12px;padding:14px 20px;
     border-bottom:1px solid var(--line-soft);background:#FAFCFE;flex-wrap:wrap;}
.tbnum{font-family:var(--display);font-weight:800;font-size:13px;color:var(--accent-ink);
     background:var(--note-bg);border-radius:6px;padding:3px 9px;letter-spacing:.4px;}
.tbname{font-family:var(--display);font-weight:700;font-size:15px;color:var(--navy);}
.tbnote{font-size:12px;color:var(--ink-soft);margin-left:auto;text-align:right;}
.tbbody{padding:18px 20px;}
.tbgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px 18px;}
.tbfield{display:flex;flex-direction:column;gap:5px;}
.tbfield label{font-size:11px;text-transform:uppercase;letter-spacing:.6px;
     font-weight:700;color:var(--ink-soft);}
.tbfield input,.tbfield select{font-family:inherit;font-size:13.5px;padding:9px 11px;
     border:1.5px solid var(--line);border-radius:8px;background:#fff;color:var(--ink);}
.tbfield input:focus,.tbfield select:focus{border-color:var(--accent);outline:none;
     box-shadow:0 0 0 3px rgba(85,200,232,.22);}
.tbhint{font-size:11.5px;color:var(--ink-faint);line-height:1.5;}
.tbfield.off{display:none;}

.tbpick{display:flex;flex-wrap:wrap;align-items:center;gap:10px;padding:12px 20px;
     background:#FAFCFE;border-bottom:1px solid var(--line-soft);}
.tbpick input[type=search]{flex:1;min-width:180px;font-family:inherit;font-size:13px;
     padding:8px 11px;border:1.5px solid var(--line);border-radius:8px;}
.tblist{max-height:340px;overflow-y:auto;padding:4px 0;}
.tbtrow{display:flex;align-items:flex-start;gap:11px;padding:9px 20px;
     border-bottom:1px solid var(--line-soft);font-size:13px;line-height:1.45;cursor:pointer;}
.tbtrow:last-child{border-bottom:none;}
.tbtrow:hover{background:#F7FAFC;}
.tbtrow input{width:17px;height:17px;accent-color:#0E5568;flex-shrink:0;
     cursor:pointer;margin-top:2px;}
.tbtmid{flex:1;min-width:0;}
.tbtt{font-weight:600;color:var(--navy);}
.tbta{color:var(--ink-soft);}
.tbtg{font-size:11px;color:var(--ink-faint);font-variant-numeric:tabular-nums;
     white-space:nowrap;}

.tbrun{display:flex;align-items:center;gap:14px;padding:13px 20px;
     border-top:1px solid var(--line);background:#FAFCFE;flex-wrap:wrap;}
.tbrunN{font-family:var(--display);font-weight:800;font-size:22px;color:var(--navy);
     font-variant-numeric:tabular-nums;}
.tbrunL{font-size:12px;color:var(--ink-soft);line-height:1.4;}
.tbbtn{font-family:inherit;font-size:13.5px;font-weight:600;padding:10px 20px;
     border-radius:8px;border:none;cursor:pointer;transition:.14s;}
.tbbtn.pri{background:var(--navy);color:#fff;}
.tbbtn.pri:hover{background:#16294E;}
.tbbtn.pri:disabled{background:var(--line);color:var(--ink-faint);cursor:not-allowed;}
.tbbtn.gh{background:#fff;color:var(--navy);border:1.5px solid var(--line);}
.tbbtn.gh:hover{border-color:var(--accent);background:var(--note-bg);}
.tbright{margin-left:auto;display:flex;gap:9px;flex-wrap:wrap;}

.tbmrow{display:flex;align-items:center;gap:12px;padding:12px 20px;
     border-bottom:1px solid var(--line-soft);flex-wrap:wrap;}
.tbmrow:last-child{border-bottom:none;}
.tbmrow.on{background:var(--note-bg);}
.tbmc{font-family:var(--display);font-weight:700;font-size:14px;color:var(--navy);}
.tbmm{display:flex;gap:5px;flex-wrap:wrap;}
.tbmn{font-size:12px;color:var(--ink-soft);font-variant-numeric:tabular-nums;}
.tbma{margin-left:auto;display:flex;gap:7px;}

.tbshelves{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:16px;}
.tbshelf{background:var(--card);border:1px solid var(--line);border-radius:12px;
     box-shadow:0 1px 3px rgba(14,28,66,.05);overflow:hidden;
     border-top:4px solid var(--accent);display:flex;flex-direction:column;}
.tbsh{padding:15px 18px 12px 18px;}
.tbsteach{font-family:var(--display);font-weight:800;font-size:17px;color:var(--navy);
     line-height:1.2;}
.tbscourse{font-size:13px;color:var(--ink-soft);margin-top:3px;}
.tbsmeta{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px;}
.tbscount{padding:0 18px 12px 18px;display:flex;align-items:baseline;gap:8px;}
.tbscount b{font-family:var(--display);font-size:26px;color:var(--navy);
     font-variant-numeric:tabular-nums;line-height:1;}
.tbscount span{font-size:12px;color:var(--ink-soft);}
.tbsbooks{border-top:1px solid var(--line-soft);flex:1;}
.tbbk{padding:11px 18px;border-bottom:1px solid var(--line-soft);}
.tbbk:last-child{border-bottom:none;}
.tbbktop{display:flex;align-items:flex-start;gap:8px;}
.tbbkt{font-size:13px;font-weight:600;color:var(--navy);line-height:1.35;}
.tbbka{font-size:12px;color:var(--ink-soft);}
.tbbked{font-size:11.5px;color:var(--ink-faint);line-height:1.5;margin-top:3px;}
.tbnolink{font-size:11px;color:var(--ink-faint);margin-top:7px;display:inline-block;}
.tbsfoot{padding:10px 18px;border-top:1px solid var(--line-soft);background:#FAFCFE;
     display:flex;gap:8px;align-items:center;flex-wrap:wrap;}

.tbstrip{display:flex;flex-wrap:wrap;align-items:center;gap:18px;background:var(--navy);
     border-radius:12px;padding:16px 20px;margin-bottom:20px;}
.tbstripN{font-family:var(--display);font-weight:800;font-size:30px;color:#fff;
     font-variant-numeric:tabular-nums;line-height:1;}
.tbstripL{font-size:12px;color:rgba(255,255,255,.72);line-height:1.5;}
.tbstripBar{flex:1;min-width:170px;height:9px;border-radius:5px;overflow:hidden;
     background:rgba(255,255,255,.16);display:flex;}
.tbstripBar i{display:block;background:var(--accent);}
.tbstripItem{display:flex;align-items:center;gap:11px;}

.tbfind{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:18px;}
.tbfind input[type=search]{flex:1;min-width:200px;font-family:inherit;font-size:13.5px;
     padding:10px 13px;border:1.5px solid var(--line);border-radius:9px;background:#fff;}
.tbfind select{font-family:inherit;font-size:13px;padding:10px 11px;
     border:1.5px solid var(--line);border-radius:9px;background:#fff;color:var(--ink);}
.tbhits{font-size:12px;color:var(--ink-soft);margin-left:auto;
     font-variant-numeric:tabular-nums;}

.tbfile{background:#0B1526;border-radius:10px;padding:15px 17px;overflow-x:auto;
     max-height:340px;overflow-y:auto;margin-top:4px;}
.tbfile pre{margin:0;font-family:ui-monospace,"Cascadia Mono",Consolas,monospace;
     font-size:12px;line-height:1.65;color:#CBD9E6;white-space:pre;}
.tbfile .k{color:#55C8E8;} .tbfile .s{color:#9BD98A;} .tbfile .n{color:#E8B96A;}
.tbsay{background:var(--note-bg);border-left:4px solid var(--accent);border-radius:8px;
     padding:13px 16px;font-size:12.5px;line-height:1.7;color:var(--ink);margin-top:14px;}
.tbsay b{color:var(--navy);}
.tbblank{padding:34px 20px;text-align:center;color:var(--ink-faint);font-size:13px;
     line-height:1.7;border:1px dashed var(--line);border-radius:12px;background:var(--card);}
.tbhide{display:none;}

"""

# NOTE ON .closest(): the Independent Reading pages once used
# tabs.closest('div'), which returns the element ITSELF and silently broke every
# genre panel. Nothing here uses .closest() on a container; element references
# are held directly. build_reference_library.py gates on that.
JS = """
(function(){
  var DATA = window.__LIB__ || [];
  var grid = document.getElementById('grid');
  var q = document.getElementById('q');
  var selGrade = document.getElementById('fGrade');
  var selShelf = document.getElementById('fShelf');
  var selAuthor = document.getElementById('fAuthor');
  var selState = document.getElementById('fState');
  var selTaught = document.getElementById('fTaught');
  var sortBtns = document.querySelectorAll('.sortbtn');
  var countEl = document.getElementById('count');
  var fab = document.getElementById('fab');
  var fabN = document.getElementById('fabN');
  var panel = document.getElementById('panel');
  var listBox = document.getElementById('listBox');

  var LS = 'optima-ela-ref-picks';
  var picked = {};
  try { picked = JSON.parse(localStorage.getItem(LS) || '{}') || {}; } catch(e){ picked = {}; }

  var sortMode = 'az';
  var cards = [];   // {el, rec}

  function nPicked(){ var n=0; for (var k in picked){ if(picked[k]) n++; } return n; }

  function savePicks(){
    try { localStorage.setItem(LS, JSON.stringify(picked)); } catch(e){}
  }

  function matches(rec){
    if (selGrade.value && rec.grade !== selGrade.value) return false;
    if (selShelf.value && rec.shelfSlug !== selShelf.value) return false;
    if (selAuthor.value && rec.authorKey !== selAuthor.value) return false;
    if (selState.value && rec.state !== selState.value) return false;
    if (selTaught.value && rec.taught !== selTaught.value) return false;
    var s = (q.value || '').trim().toLowerCase();
    if (s && rec.k.indexOf(s) === -1) return false;
    return true;
  }

  function cmp(a, b){
    if (sortMode === 'grade'){
      var ga = a.rec.gradeNum, gb = b.rec.gradeNum;
      if (ga !== gb) return ga - gb;
      return a.rec.sortTitle < b.rec.sortTitle ? -1 : 1;
    }
    if (sortMode === 'author'){
      if (a.rec.authorKey !== b.rec.authorKey)
        return a.rec.authorKey < b.rec.authorKey ? -1 : 1;
      return a.rec.sortTitle < b.rec.sortTitle ? -1 : 1;
    }
    if (sortMode === 'shelf'){
      if (a.rec.shelf !== b.rec.shelf) return a.rec.shelf < b.rec.shelf ? -1 : 1;
      return a.rec.sortTitle < b.rec.sortTitle ? -1 : 1;
    }
    return a.rec.sortTitle < b.rec.sortTitle ? -1 : 1;
  }

  function headingFor(rec){
    if (sortMode === 'grade') return 'Grade ' + rec.grade;
    if (sortMode === 'shelf') return rec.shelf;
    if (sortMode === 'author') return (rec.authorDisplay || 'Unattributed');
    var c = rec.sortTitle.charAt(0).toUpperCase();
    return /[A-Z]/.test(c) ? c : '#';
  }

  function render(){
    var vis = [];
    for (var i=0;i<cards.length;i++){
      if (matches(cards[i].rec)) vis.push(cards[i]);
    }
    vis.sort(cmp);

    // Detach everything, then re-append in order under fresh headings.
    while (grid.firstChild) grid.removeChild(grid.firstChild);

    if (!vis.length){
      var n = document.createElement('div');
      n.className = 'noresult';
      n.textContent = 'No titles match those filters.';
      grid.appendChild(n);
    } else {
      var lastHead = null;
      for (var j=0;j<vis.length;j++){
        var h = headingFor(vis[j].rec);
        if (h !== lastHead){
          var hd = document.createElement('div');
          hd.className = 'secthead';
          hd.appendChild(document.createTextNode(h));
          grid.appendChild(hd);
          lastHead = h;
        }
        grid.appendChild(vis[j].el);
      }
    }
    countEl.textContent = vis.length + ' of ' + cards.length + ' titles';
    fabN.textContent = nPicked();
    fab.style.display = nPicked() ? 'block' : 'none';
  }

  function esc(s){
    return String(s == null ? '' : s)
      .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  function lineFor(rec){
    var bits = [];
    if (rec.translator) bits.push('trans. ' + esc(rec.translator));
    if (rec.editor) bits.push('ed. ' + esc(rec.editor));
    if (rec.publisher) bits.push(esc(rec.publisher));
    if (rec.editionYear) bits.push(esc(rec.editionYear));
    if (rec.isbn) bits.push('ISBN ' + esc(rec.isbn));
    var m = bits.length ? '<span class="m">' + bits.join(' &middot; ') + '</span>' : '';
    var links = [];
    if (rec.buyUrl) links.push('<a href="'+esc(rec.buyUrl)+'" target="_blank" rel="noopener">purchase</a>');
    if (rec.freeUrl) links.push('<a href="'+esc(rec.freeUrl)+'" target="_blank" rel="noopener">'
      + (rec.state === 'identical' ? 'free text' : 'similar version free') + '</a>');
    var lk = links.length ? '<span class="m">' + links.join(' &nbsp;|&nbsp; ') + '</span>' : '';
    return '<div class="li"><b>' + esc(rec.title) + '</b>'
      + (rec.authorDisplay ? ' &mdash; ' + esc(rec.authorDisplay) : '')
      + (rec.year ? ' <span class="m" style="display:inline">(' + esc(rec.year) + ')</span>' : '')
      + m + lk + '</div>';
  }

  function buildList(){
    var buy = [], sim = [], free = [];
    for (var i=0;i<cards.length;i++){
      var r = cards[i].rec;
      if (!picked[r.id]) continue;
      if (r.state === 'none') buy.push(r);
      else if (r.state === 'similar') sim.push(r);
      else free.push(r);
    }
    function sec(cls, title, note, arr){
      if (!arr.length) return '';
      arr.sort(function(a,b){ return a.sortTitle < b.sortTitle ? -1 : 1; });
      var h = '<div class="grp ' + cls + '"><h3>' + title + ' (' + arr.length + ')</h3>';
      if (note) h += '<div class="lede" style="margin:-4px 0 10px 0;">' + note + '</div>';
      for (var k=0;k<arr.length;k++) h += lineFor(arr[k]);
      return h + '</div>';
    }
    var total = buy.length + sim.length + free.length;
    var head = '<h2>My reading list</h2>'
      + '<div class="lede">' + total + ' title' + (total===1?'':'s')
      + ' selected. Students need to buy ' + buy.length
      + '; ' + (free.length + sim.length) + ' can be read free.</div>';
    var body = sec('', 'Students must purchase',
        'In copyright. A free PDF found online is not a licence.', buy)
      + sec('s', 'Free, but a different version',
        'The free text is a different translation or edition from the one the book list specifies. Fine for reference; check before assigning by page or line.', sim)
      + sec('f', 'Free, same text',
        'Public domain, and the free text is the assigned text.', free);
    if (!total) body = '<div class="empty">Nothing selected yet. Tick the box on any card.</div>';
    listBox.innerHTML = head + body
      + '<div class="pbtns">'
      + '<button class="pbtn primary" id="pPrint">Print / Save as PDF</button>'
      + '<button class="pbtn" id="pCopy">Copy as text</button>'
      + '<button class="pbtn" id="pClear">Clear selection</button>'
      + '<button class="pbtn" id="pClose">Close</button>'
      + '</div>';

    document.getElementById('pPrint').onclick = function(){ window.print(); };
    document.getElementById('pClose').onclick = closePanel;
    document.getElementById('pClear').onclick = function(){
      picked = {}; savePicks();
      for (var i=0;i<cards.length;i++){
        var cb = cards[i].el.querySelector('.cb');
        if (cb) cb.checked = false;
        cards[i].el.className = 'book';
      }
      buildList(); render();
    };
    document.getElementById('pCopy').onclick = function(){
      var txt = listBox.innerText.replace(/\\n{3,}/g, '\\n\\n');
      if (navigator.clipboard) navigator.clipboard.writeText(txt);
      this.textContent = 'Copied';
      var b = this;
      setTimeout(function(){ b.textContent = 'Copy as text'; }, 1400);
    };
  }

  function openPanel(){ buildList(); panel.className = 'panel open'; }
  function closePanel(){ panel.className = 'panel'; }

  // ---- wire up
  var nodes = grid.querySelectorAll('.book');
  for (var i=0;i<nodes.length;i++){
    var el = nodes[i];
    var idx = parseInt(el.getAttribute('data-i'), 10);
    var rec = DATA[idx];
    if (!rec) continue;
    cards.push({el: el, rec: rec});
    var cb = el.querySelector('.cb');
    if (cb){
      if (picked[rec.id]){ cb.checked = true; el.className = 'book sel'; }
      cb.addEventListener('change', (function(el, rec, cb){
        return function(){
          picked[rec.id] = cb.checked;
          if (!cb.checked) delete picked[rec.id];
          el.className = cb.checked ? 'book sel' : 'book';
          savePicks();
          fabN.textContent = nPicked();
          fab.style.display = nPicked() ? 'block' : 'none';
        };
      })(el, rec, cb));
    }
  }

  q.addEventListener('input', render);
  selGrade.addEventListener('change', render);
  selShelf.addEventListener('change', render);
  selAuthor.addEventListener('change', render);
  selState.addEventListener('change', render);
  selTaught.addEventListener('change', render);
  for (var s=0;s<sortBtns.length;s++){
    sortBtns[s].addEventListener('click', (function(btn){
      return function(){
        sortMode = btn.getAttribute('data-sort');
        for (var t=0;t<sortBtns.length;t++)
          sortBtns[t].setAttribute('aria-pressed', sortBtns[t] === btn ? 'true' : 'false');
        render();
      };
    })(sortBtns[s]));
  }
  fab.addEventListener('click', openPanel);
  panel.addEventListener('click', function(ev){
    if (ev.target === panel) closePanel();
  });
  document.addEventListener('keydown', function(ev){
    if (ev.key === 'Escape') closePanel();
  });

  // Reveal the controls only now that the script has run, so a JS failure
  // leaves the full linear list visible rather than an empty page.
  var jo = document.querySelectorAll('.js-only');
  for (var z=0;z<jo.length;z++) jo[z].style.display = '';

  render();
})();
"""
