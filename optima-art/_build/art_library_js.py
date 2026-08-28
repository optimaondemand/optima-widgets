# -*- coding: utf-8 -*-
"""Behaviour for the Art Reference Library.

The data is inlined into the page as ART, so the widget works from a local disk copy and
inside a Canvas iframe with no fetch. Rendering is a full re-render of the grid on every
filter change: 529 cards is small enough that this is instant and leaves no stale state,
which is worth more than a diffing scheme nobody will maintain.

IMAGES ARE LAZY. Only 17 of 529 have one, but each is up to 1600px, so every img carries
loading="lazy" plus explicit width and height. Without the dimensions the grid reflows as
each plate arrives and the page jumps under the teacher's cursor while they scroll.
"""

JS = """
(function(){
  "use strict";
  var STORE = "optima-art-library-filters";

  var state = {q:"", avail:"", course:"", movement:"", subject:"", sort:"default"};
  var bundle = [];   // work ids the teacher has picked, in pick order

  function norm(s){
    return (s||"").toString().toLowerCase()
      .normalize("NFD").replace(/[\\u0300-\\u036f]/g,"");
  }

  // one flat searchable string per work, built once
  ART.works.forEach(function(w){
    w._hay = norm([w.title, w.creator_full, w.creator_filed, w.date, w.disposition_label,
                   (w.courses||[]).join(" "), (w.units||[]).join(" "),
                   (w.tags||[]).map(function(t){return t.label + " " + t.code;}).join(" ")
                  ].join(" "));
    w._movement = (w.tags||[]).filter(function(t){return t.scheme === "art.movement";})
                              .map(function(t){return t.label;})[0] || "";
    w._concepts = (w.tags||[]).filter(function(t){return t.scheme === "concept";});
    w._subjects = w._concepts.map(function(t){return t.discipline;})
                             .filter(function(d, i, a){return d && a.indexOf(d) === i;});
  });

  function availKey(w){
    if (w.disposition === "publish") return "image";
    if (w.jstor_url) return "link";
    return "neither";
  }

  function matches(w){
    if (state.q && w._hay.indexOf(norm(state.q)) === -1) return false;
    if (state.avail && availKey(w) !== state.avail) return false;
    if (state.course && (w.courses||[]).indexOf(state.course) === -1) return false;
    if (state.movement && w._movement !== state.movement) return false;
    if (state.subject && w._subjects.indexOf(state.subject) === -1) return false;
    return true;
  }

  function esc(s){
    return (s == null ? "" : String(s))
      .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
      .replace(/"/g,"&quot;");
  }

  function badgeFor(w){
    // The label comes from the contract, not from a switch here, because "research"
    // covers three different situations and one of them - a Mondrian recorded as 1921 -
    // is not an unconfirmed date at all. Hardcoding "Date unconfirmed" told a teacher to
    // go looking for something the record already had.
    var cls = w.disposition === "publish" ? "pub"
            : (w.disposition === "research" && w.hold_reason !== "modern-band") ? "res"
            : "link";
    return '<span class="badge ' + cls + '">' + esc(w.disposition_label) + '</span>';
  }

  function plateFor(w){
    if (w.image){
      return '<div class="plate"><img src="' + esc(w.image) + '" alt="' +
        esc((w.creator ? w.creator + ", " : "") + (w.title||"")) +
        '" loading="lazy" decoding="async" width="' + (w.image_w||800) +
        '" height="' + (w.image_h||600) + '"></div>';
    }
    return '<div class="noplate">No image published</div>';
  }

  function cardFor(w){
    var h = '<article class="card">' + plateFor(w) + '<div class="body">';
    h += badgeFor(w);
    h += '<h3 class="t">' + esc(w.title || "Untitled") + '</h3>';
    if (w.creator){
      h += '<p class="c">' + esc(w.creator) + '</p>';
    } else if (w.creator_filed){
      // filename-derived, so it is what a course called it, not an attribution
      h += '<p class="c"><em>Filed as ' + esc(w.creator_filed) + '</em></p>';
    } else {
      h += '<p class="c"><em>Artist not recorded</em></p>';
    }
    if (w.date) h += '<p class="d">' + esc(w.date) + '</p>';
    // movements come from folder names and are wrong often enough to matter: a Seurat
    // filed under Neoclassicism, a 1501 illumination filed Medieval. Say "filed under"
    // rather than printing a period as though it were established.
    if (w._movement) h += '<p class="d">Filed under ' + esc(w._movement) + '</p>';
    if (w._concepts.length){
      h += '<div class="cpills">' + w._concepts.map(function(t){
        // title attribute carries the evidence, so a teacher who doubts a link can check
        return '<span class="cpill" title="' + esc(t.discipline + ' - ' + (t.asserted_by||'')) +
               '">' + esc(t.label) + '</span>';
      }).join("") + '</div>';
    }
    if (w.disposition !== "publish" && w.why)
      h += '<p class="why">' + esc(w.why) + '</p>';
    h += '<div class="foot">';
    if (w.jstor_url)
      h += '<a class="jstor" href="' + esc(w.jstor_url) +
           '" target="_blank" rel="noopener">View on JSTOR</a>';
    if (w.image)
      h += '<button class="copybtn" data-url="' + esc(w.image) +
           '">Copy image URL</button>';
    h += '<button class="addbtn' + (bundle.indexOf(w.id) > -1 ? ' in' : '') +
         '" data-add="' + esc(w.id) + '">' +
         (bundle.indexOf(w.id) > -1 ? 'In lesson' : 'Add to lesson') + '</button>';
    if ((w.courses||[]).length)
      h += '<span class="uses">' + esc(w.courses.join(", ")) + '</span>';
    h += '</div></div></article>';
    return h;
  }

  function sortRows(rows){
    var s = state.sort;
    if (s === "artist")
      return rows.sort(function(a,b){
        return norm(a.creator||"zzz").localeCompare(norm(b.creator||"zzz")); });
    if (s === "title")
      return rows.sort(function(a,b){
        return norm(a.title).localeCompare(norm(b.title)); });
    if (s === "oldest")
      return rows.sort(function(a,b){
        return (a.year==null?99999:a.year) - (b.year==null?99999:b.year); });
    if (s === "newest")
      return rows.sort(function(a,b){
        return (b.year==null?-99999:b.year) - (a.year==null?-99999:a.year); });
    return rows;
  }

  function byId(id){
    for (var i = 0; i < ART.works.length; i++)
      if (ART.works[i].id === id) return ART.works[i];
    return null;
  }

  function lessonBlock(){
    // A paste-ready plain-text block. Deliberately not HTML: a teacher pastes this into
    // a lesson plan, an email or a Canvas rich-text box, and plain text survives all three.
    var lines = ["Optima Art Reference Library - lesson selection",
                 "Generated " + new Date().toISOString().slice(0, 10),
                 ""];
    bundle.forEach(function(id, i){
      var w = byId(id);
      if (!w) return;
      lines.push((i + 1) + ". " + (w.title || "Untitled"));
      lines.push("   Artist:  " + (w.creator_full || w.creator ||
                                   (w.creator_filed ? "filed as " + w.creator_filed
                                                    : "not recorded")));
      if (w.date) lines.push("   Date:    " + w.date);
      if (w.material) lines.push("   Medium:  " + w.material);
      if (w._concepts && w._concepts.length)
        lines.push("   Subject: " + w._concepts.map(function(t){return t.label;}).join(", "));
      if (w.image){
        lines.push("   Image:   " + w.image);
        lines.push("   Licence: " + (w.licence || "free to use"));
      } else {
        lines.push("   Image:   not published - " + (w.why || "see the library"));
      }
      if (w.jstor_url) lines.push("   JSTOR:   " + w.jstor_url);
      if ((w.courses || []).length)
        lines.push("   Used in: " + w.courses.join(", "));
      lines.push("");
    });
    lines.push("Image links are free to use. JSTOR links need an Optima login.");
    return lines.join("\\n");
  }

  function renderTray(){
    var tray = document.getElementById("tray");
    var on = bundle.length > 0;
    tray.classList.toggle("open", on);
    document.body.classList.toggle("hastray", on);
    if (!on) return;
    document.getElementById("traycount").innerHTML =
      "<span>" + bundle.length + "</span> in this lesson";
    document.getElementById("traynames").textContent =
      bundle.map(function(id){ var w = byId(id); return w ? (w.title || "Untitled") : id; })
            .join("  -  ");
  }

  function render(){
    var rows = sortRows(ART.works.filter(matches));
    var grid = document.getElementById("grid");
    if (!rows.length){
      grid.innerHTML = '<div class="empty"><b>Nothing matches that</b>' +
        'Try a shorter search, or clear the filters.</div>';
    } else {
      grid.innerHTML = rows.map(cardFor).join("");
    }
    var withImg = rows.filter(function(w){return !!w.image;}).length;
    document.getElementById("resultline").innerHTML =
      "Showing <b>" + rows.length + "</b> of " + ART.works.length +
      " works &middot; <b>" + withImg + "</b> with a published image";
    document.querySelectorAll(".chip[data-avail]").forEach(function(c){
      c.setAttribute("aria-pressed", String(c.dataset.avail === state.avail));
    });
    // the subject chips are styled off [aria-pressed="true"], so failing to set this
    // left the active subject looking inactive as well as reading wrong to a screen reader
    document.querySelectorAll(".subj[data-subject]").forEach(function(c){
      c.setAttribute("aria-pressed", String(c.dataset.subject === state.subject));
    });
    save();
  }

  function save(){
    try {
      localStorage.setItem(STORE, JSON.stringify({state: state, bundle: bundle}));
    } catch(e){}
  }

  function wire(){
    var q = document.getElementById("q");
    q.addEventListener("input", function(){ state.q = q.value; render(); });

    document.querySelectorAll(".chip[data-avail]").forEach(function(c){
      c.addEventListener("click", function(){
        state.avail = (state.avail === c.dataset.avail) ? "" : c.dataset.avail;
        render();
      });
    });

    ["course","movement","sort"].forEach(function(k){
      var el = document.getElementById(k);
      if (el) el.addEventListener("change", function(){ state[k] = el.value; render(); });
    });

    document.querySelectorAll(".subj[data-subject]").forEach(function(c){
      c.addEventListener("click", function(){
        state.subject = (state.subject === c.dataset.subject) ? "" : c.dataset.subject;
        render();
      });
    });

    document.getElementById("traycopy").addEventListener("click", function(){
      var text = lessonBlock();
      var btn = this;
      var done = function(){
        btn.textContent = "Copied";
        setTimeout(function(){ btn.textContent = "Copy lesson block"; }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText){
        navigator.clipboard.writeText(text).then(done, function(){ window.prompt("Copy", text); });
      } else { window.prompt("Copy", text); }
    });

    document.getElementById("trayclear").addEventListener("click", function(){
      bundle = [];
      save();
      renderTray();
      render();
    });

    document.getElementById("gear").addEventListener("click", function(){
      document.getElementById("panel").classList.toggle("open");
    });

    // event delegation: the grid is replaced wholesale on every render, so a listener
    // bound to a button would be thrown away with it
    document.getElementById("grid").addEventListener("click", function(ev){
      var add = ev.target.closest(".addbtn");
      if (add){
        var id = add.dataset.add;
        var at = bundle.indexOf(id);
        if (at > -1) bundle.splice(at, 1); else bundle.push(id);
        save();
        add.classList.toggle("in", bundle.indexOf(id) > -1);
        add.textContent = bundle.indexOf(id) > -1 ? "In lesson" : "Add to lesson";
        renderTray();
        return;
      }
      var b = ev.target.closest(".copybtn");
      if (!b) return;
      var url = b.dataset.url;
      var done = function(){
        b.textContent = "Copied";
        b.classList.add("done");
        setTimeout(function(){
          b.textContent = "Copy image URL"; b.classList.remove("done"); }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText){
        navigator.clipboard.writeText(url).then(done, function(){ window.prompt("Copy this URL", url); });
      } else {
        window.prompt("Copy this URL", url);
      }
    });
  }

  function restore(){
    try {
      var saved = JSON.parse(localStorage.getItem(STORE) || "{}");
      // the stored shape changed when the lesson tray was added; tolerate the old one
      var st = saved.state || saved;
      Object.keys(state).forEach(function(k){
        if (typeof st[k] === "string") state[k] = st[k];
      });
      if (Array.isArray(saved.bundle))
        // drop ids that no longer exist rather than rendering a phantom count
        bundle = saved.bundle.filter(function(id){ return !!byId(id); });
    } catch(e){}
    var q = document.getElementById("q");
    if (q) q.value = state.q;
    ["course","movement","sort"].forEach(function(k){
      var el = document.getElementById(k);
      // a saved value whose option no longer exists must not silently filter to nothing
      if (el && !Array.prototype.some.call(el.options,
            function(o){ return o.value === state[k]; })) state[k] = "";
      if (el) el.value = state[k];
    });
  }

  restore();
  wire();
  renderTray();
  render();
})();
"""
