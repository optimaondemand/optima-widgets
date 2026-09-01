# -*- coding: utf-8 -*-
"""Behaviour for the Music Reference Library.

The contract is inlined as MUSIC, so the page works from a local disk copy and inside a
Canvas iframe with no fetch. Every filter change re-renders the whole grid: 155 cards is
small enough that this is instant and leaves no stale state.

NOTHING LOADS FROM YOUTUBE UNTIL ASKED. Thumbnails are lazy and carry explicit width and
height so a late arrival cannot reflow the grid under a teacher's cursor, and the player
itself is only injected on click -- as a youtube-nocookie embed, so browsing the
catalogue does not build a watch history for whoever opens the page.

A dead video gets no player at all. Two of these are still linked from live Canvas
courses, and offering a play button that does nothing would hide exactly the fact the
page exists to surface.
"""

JS = """
(function(){
  "use strict";
  var STORE = "optima-music-library-filters";

  var state = {q:"", status:"", course:"", genre:"", topic:"", xref:"", sort:"default"};
  var playlist = [];   // video ids the teacher has picked, in pick order

  var CMAP = {};
  MUSIC.courses.forEach(function(c){ CMAP[c.id] = c; });
  var GENRE_LABEL = (MUSIC.labels || {})["music.genre"] || {};

  function norm(s){
    return (s||"").toString().toLowerCase()
      .normalize("NFD").replace(/[\\u0300-\\u036f]/g,"");
  }

  function esc(s){
    return (s == null ? "" : String(s))
      .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
      .replace(/"/g,"&quot;");
  }

  // one flat searchable string per video, built once. Course NAMES go in as well as ids,
  // so a teacher searching "world" finds the Music of the World videos without knowing
  // that the catalogue calls that course motw.
  MUSIC.videos.forEach(function(v){
    var cnames = (v.courses||[]).map(function(id){
      return CMAP[id] ? CMAP[id].name + " " + CMAP[id].short + " " + CMAP[id].code : id; });
    v._hay = norm([v.title, v.channel, (v.courses||[]).join(" "), cnames.join(" "),
                   (v.lessons||[]).map(function(l){return l.page_title;}).join(" "),
                   (v.tags||[]).map(function(t){return t.label + " " + t.code;}).join(" "),
                   ((v.cross_refs||{}).art||[]).map(function(h){return h.title + " " + (h.creator||"");}).join(" "),
                   ((v.cross_refs||{}).ela||[]).map(function(h){return h.title + " " + (h.author||"");}).join(" ")
                  ].join(" "));
    v._topics = (v.tags||[]).map(function(t){ return t.scheme + ":" + t.code; });
    v._genres = (v.tags||[]).filter(function(t){ return t.scheme === "music.genre"; })
                            .map(function(t){ return t.code; });
    v._uses = (v.lessons||[]).length;
    v._art = ((v.cross_refs||{}).art||[]).length;
    v._ela = ((v.cross_refs||{}).ela||[]).length;
  });

  function matches(v){
    if (state.q && v._hay.indexOf(norm(state.q)) === -1) return false;
    if (state.status && v.disposition !== state.status) return false;
    if (state.course && (v.courses||[]).indexOf(state.course) === -1) return false;
    if (state.genre && v._genres.indexOf(state.genre) === -1) return false;
    if (state.topic && v._topics.indexOf(state.topic) === -1) return false;
    if (state.xref === "art" && !v._art) return false;
    if (state.xref === "ela" && !v._ela) return false;
    return true;
  }

  function frameFor(v){
    if (v.state !== "ok"){
      var why = v.state === "deleted" ? "Deleted from YouTube"
              : v.state === "private" ? "Made private on YouTube"
              : "Unavailable (" + v.state + ")";
      return '<div class="noframe">' + esc(why) + '</div>';
    }
    var thumb = v.thumb || ("https://i.ytimg.com/vi/" + v.id + "/hqdefault.jpg");
    return '<div class="frame" data-frame="' + esc(v.id) + '">' +
      '<img src="' + esc(thumb) + '" alt="" loading="lazy" decoding="async" ' +
        'width="480" height="360">' +
      '<button class="playbtn" type="button" data-play="' + esc(v.id) + '" ' +
        'aria-label="Play ' + esc(v.title || v.id) + ' here">' +
        '<span class="tri">&#9654;</span></button></div>';
  }

  function courseBadges(v){
    if (!(v.courses||[]).length) return "";
    var mods = {};
    (v.lessons||[]).forEach(function(l){
      if (l.module == null) return;
      mods[l.course] = mods[l.course] || {};
      mods[l.course][l.module] = 1;
    });
    return '<div class="courses">' + v.courses.map(function(id){
      var c = CMAP[id], n = mods[id] ? Object.keys(mods[id]).length : 0;
      var soft = v.attribution !== "build" ? " soft" : "";
      return '<span class="cb' + soft + '" title="' + esc(c ? c.name : id) + '">' +
        esc(c ? c.short : id) + (n ? " &middot; " + n + (n === 1 ? " module" : " modules") : "") +
        '</span>';
    }).join("") + '</div>';
  }

  function usesFor(v){
    var ls = v.lessons || [];
    if (!ls.length) return "";
    return '<details class="uses"><summary>' + ls.length +
      (ls.length === 1 ? " lesson uses it" : " lessons use it") +
      '</summary><ul>' + ls.map(function(l){
        var c = CMAP[l.course];
        // Three of the harvested citations are the harvester's own content-map page
        // rather than a lesson, and one is a raw filename. Printing those at a teacher
        // reads as a bug, so the module line says what is actually known and the page
        // string stays in the hover.
        var where = l.module == null
          ? '<b>Module not recorded</b>'
          : '<b>Module ' + esc(l.module) + '</b>';
        return '<li title="' + esc(l.page_title || "") + '">' +
          esc(c ? c.short : l.course) + " &middot; " + where + '</li>';
      }).join("") + '</ul></details>';
  }

  function pillsFor(v){
    if (!(v.tags||[]).length) return "";
    return '<div class="pills">' + v.tags.map(function(t){
      var cls = "pill" + (t.scheme === "concept" ? " concept" : "") +
                (t.scope === "lesson" ? " lessonscope" : "");
      // The hover carries the evidence AND the scope, because "Harmony" on a video that
      // is not about harmony is right only in the sense that the lesson around it is.
      var tip = (t.scope === "video" ? "This video is: " : "The lesson using it is about: ") +
                t.label + "  --  asserted by " + (t.asserted_by || "no evidence recorded");
      return '<span class="' + cls + '" title="' + esc(tip) + '">' + esc(t.label) + '</span>';
    }).join("") + '</div>';
  }

  function xrefFor(v){
    var x = v.cross_refs || {}, out = "";
    if ((x.art||[]).length){
      out += '<p class="xref"><b>Also in the art library</b>' +
        x.art.map(function(h){
          var name = esc(h.title) + (h.creator ? ' <span>&middot; ' + esc(h.creator) + '</span>' : "");
          if (h.image) return '<a href="' + esc(h.image) + '" target="_blank" rel="noopener">' + name + '</a>';
          if (h.jstor_url) return '<a href="' + esc(h.jstor_url) + '" target="_blank" rel="noopener">' + name + '</a>';
          return name;
        }).join("<br>") + '</p>';
    }
    if ((x.ela||[]).length){
      out += '<p class="xref"><b>Also in the ELA library</b>' +
        x.ela.map(function(h){
          return esc(h.title) + (h.author ? ' <span>&middot; ' + esc(h.author) + '</span>' : "");
        }).join("<br>") + '</p>';
    }
    return out;
  }

  function cardFor(v){
    // No status badge. "In use", "Live in Canvas" and "Dropped in the rebuild" are
    // build bookkeeping: true of the catalogue, meaningless to someone looking for
    // something to listen to. A link that does not play is different -- that is a
    // warning, not a status, so it stays, styled as one.
    var h = '<article class="card" data-id="' + esc(v.id) + '">' + frameFor(v) +
            '<div class="body">';
    h += '<h3 class="t">' + esc(v.title || "Title not resolved") + '</h3>';
    if (v.channel){
      h += '<p class="ch">' + (v.channel_url
        ? '<a href="' + esc(v.channel_url) + '" target="_blank" rel="noopener">' +
          esc(v.channel) + '</a>'
        : esc(v.channel)) + '</p>';
    } else {
      h += '<p class="ch"><em>Channel not resolved</em></p>';
    }
    if (v.state !== "ok")
      h += '<p class="warn">This link no longer plays' +
           (v.state === "deleted" ? " — the channel deleted it"
            : v.state === "private" ? " — it was made private" : "") + '.</p>';
    h += courseBadges(v);
    if (v.attribution === "legacy-pool")
      h += '<p class="ch"><em>In the old exports of ' +
           esc((v.legacy_in||[]).map(function(id){
             return CMAP[id] ? CMAP[id].short : id; }).join(", ")) +
           ', but in no rebuilt module</em></p>';
    h += usesFor(v);
    h += pillsFor(v);
    h += xrefFor(v);
    h += '<div class="foot">';
    h += '<a class="watch" href="' + esc(v.url) + '" target="_blank" rel="noopener">' +
         (v.state === "ok" ? "Open on YouTube" : "Check the link") + '</a>';
    h += '<button class="copybtn" data-url="' + esc(v.url) + '">Copy link</button>';
    h += '<button class="addbtn' + (playlist.indexOf(v.id) > -1 ? ' in' : '') +
         '" data-add="' + esc(v.id) + '">' +
         (playlist.indexOf(v.id) > -1 ? 'In playlist' : 'Add to playlist') + '</button>';
    h += '</div></div></article>';
    return h;
  }

  function moduleIn(v, course){
    // lowest module this video appears in, within one course. A video cited only by a
    // content map has no module and sorts after everything that has one.
    var best = null;
    (v.lessons||[]).forEach(function(l){
      if (l.course !== course || l.module == null) return;
      if (best === null || l.module < best) best = l.module;
    });
    return best === null ? 9999 : best;
  }

  function sortRows(rows){
    var s = state.sort;
    if (s === "title")
      return rows.sort(function(a,b){
        return norm(a.title||"zzz").localeCompare(norm(b.title||"zzz")); });
    if (s === "channel")
      return rows.sort(function(a,b){
        return norm(a.channel||"zzz").localeCompare(norm(b.channel||"zzz")) ||
               norm(a.title||"").localeCompare(norm(b.title||"")); });
    if (s === "uses")
      return rows.sort(function(a,b){ return b._uses - a._uses ||
               norm(a.title||"").localeCompare(norm(b.title||"")); });
    // Browsing one course means walking it in teaching order, so the default sort
    // becomes module order as soon as a course shelf is open. No extra control and no
    // surprise: pick a course and the shelf is in the order the course teaches it.
    if (s === "default" && state.course){
      var c = state.course;
      return rows.sort(function(a,b){
        return moduleIn(a,c) - moduleIn(b,c) ||
               norm(a.title||"zzz").localeCompare(norm(b.title||"zzz")); });
    }
    // otherwise: everything usable first, dead links last, then by title. Nobody
    // scanning the shelf should have to step over two broken records to reach it.
    // Ranks start at 1, not 0: with a 0 the fallback `rank[x] || 4` fired on the most
    // common case in the catalogue and sank all 141 in-use videos below the 6 dropped
    // ones. Every value here must stay truthy.
    var rank = {"in-use":1, "live-canvas":2, "dropped-in-renovation":3, "unknown":4,
                "dead-link":5};
    return rows.sort(function(a,b){
      return (rank[a.disposition]||4) - (rank[b.disposition]||4) ||
             norm(a.title||"zzz").localeCompare(norm(b.title||"zzz")); });
  }

  function byId(id){
    for (var i = 0; i < MUSIC.videos.length; i++)
      if (MUSIC.videos[i].id === id) return MUSIC.videos[i];
    return null;
  }

  function playlistText(){
    // Plain text, not HTML: a teacher pastes this into a lesson plan, an email or a
    // Canvas box, and plain text survives all three.
    var lines = ["Optima Music Reference Library - listening list",
                 "Generated " + new Date().toISOString().slice(0, 10),
                 ""];
    playlist.forEach(function(id, i){
      var v = byId(id);
      if (!v) return;
      lines.push((i + 1) + ". " + (v.title || v.id));
      lines.push("   Channel: " + (v.channel || "not resolved"));
      lines.push("   Link:    " + v.url);
      if ((v.courses||[]).length)
        lines.push("   Used in: " + v.courses.map(function(c){
          return CMAP[c] ? CMAP[c].name : c; }).join("; "));
      if ((v.tags||[]).length)
        lines.push("   Topics:  " + v.tags.map(function(t){return t.label;}).join(", "));
      if (v.state !== "ok")
        lines.push("   WARNING: this link no longer works (" + v.state + ")");
      lines.push("");
    });
    lines.push("Videos are linked, never re-hosted. Check each link before class.");
    return lines.join("\\n");
  }

  function embedHtml(){
    // Paste-ready for a Canvas page. nocookie, one iframe per video, a caption above it
    // so the page still says what the video is if the embed is blocked.
    var out = [];
    playlist.forEach(function(id){
      var v = byId(id);
      if (!v || v.state !== "ok") return;
      out.push('<p style="margin:22px 0 6px;font-family:Arial,Helvetica,sans-serif;' +
        'font-weight:bold;color:#0f2340;">' + esc(v.title || "") + '</p>');
      out.push('<iframe width="640" height="360" src="' + esc(v.embed_url) +
        '" title="' + esc(v.title || "") + '" frameborder="0" ' +
        'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; ' +
        'picture-in-picture" allowfullscreen></iframe>');
    });
    if (!out.length) return "";
    return out.join("\\n");
  }

  function copy(text, btn, doneLabel, restoreLabel){
    var done = function(){
      btn.textContent = doneLabel;
      setTimeout(function(){ btn.textContent = restoreLabel; }, 1600);
    };
    if (navigator.clipboard && navigator.clipboard.writeText){
      navigator.clipboard.writeText(text).then(done, function(){ window.prompt("Copy", text); });
    } else { window.prompt("Copy", text); }
  }

  function renderTray(){
    var tray = document.getElementById("tray");
    var on = playlist.length > 0;
    tray.classList.toggle("open", on);
    document.body.classList.toggle("hastray", on);
    if (!on) return;
    document.getElementById("traycount").innerHTML =
      "<span>" + playlist.length + "</span> in this list";
    document.getElementById("traynames").textContent =
      playlist.map(function(id){ var v = byId(id); return v ? (v.title || id) : id; })
              .join("  -  ");
    var live = playlist.filter(function(id){
      var v = byId(id); return v && v.state === "ok"; }).length;
    var eb = document.getElementById("trayembed");
    eb.disabled = live === 0;
    eb.title = live === playlist.length ? "" :
      (playlist.length - live) + " of these have dead links and are left out of the embed";
  }

  function render(){
    var rows = sortRows(MUSIC.videos.filter(matches));
    var grid = document.getElementById("grid");
    if (!rows.length){
      grid.innerHTML = '<div class="empty"><b>Nothing matches that</b>' +
        'Try a shorter search, or clear the filters.</div>';
    } else {
      grid.innerHTML = rows.map(cardFor).join("");
    }
    var dead = rows.filter(function(v){return v.state !== "ok";}).length;
    var shelf = [];
    if (state.course && CMAP[state.course]) shelf.push(CMAP[state.course].name);
    if (state.genre) shelf.push(GENRE_LABEL[state.genre] || state.genre);
    document.getElementById("resultline").innerHTML =
      (shelf.length ? "<b>" + shelf.map(esc).join(" &middot; ") + "</b> &mdash; " : "") +
      "showing <b>" + rows.length + "</b> of " + MUSIC.videos.length + " videos" +
      (state.course && state.sort === "default" ? ", in module order" : "") +
      (dead ? " &middot; <b>" + dead + "</b> with a link that no longer works" : "");
    [["data-status","status"],["data-course","course"],["data-genre","genre"],
     ["data-xref","xref"]].forEach(function(pair){
      document.querySelectorAll("[" + pair[0] + "]").forEach(function(c){
        c.setAttribute("aria-pressed",
          String(c.dataset[pair[1]] === state[pair[1]] && state[pair[1]] !== ""));
      });
    });
    save();
  }

  function save(){
    try {
      localStorage.setItem(STORE, JSON.stringify({state: state, playlist: playlist}));
    } catch(e){}
  }

  function wire(){
    var q = document.getElementById("q");
    q.addEventListener("input", function(){ state.q = q.value; render(); });

    document.querySelectorAll("[data-status]").forEach(function(c){
      c.addEventListener("click", function(){
        state.status = (state.status === c.dataset.status) ? "" : c.dataset.status;
        render();
      });
    });

    document.querySelectorAll("[data-course]").forEach(function(c){
      c.addEventListener("click", function(){
        state.course = (state.course === c.dataset.course) ? "" : c.dataset.course;
        render();
      });
    });

    document.querySelectorAll("[data-genre]").forEach(function(c){
      c.addEventListener("click", function(){
        state.genre = (state.genre === c.dataset.genre) ? "" : c.dataset.genre;
        render();
      });
    });

    document.querySelectorAll(".subj[data-xref]").forEach(function(c){
      c.addEventListener("click", function(){
        state.xref = (state.xref === c.dataset.xref) ? "" : c.dataset.xref;
        render();
      });
    });

    ["topic","sort"].forEach(function(k){
      var el = document.getElementById(k);
      if (el) el.addEventListener("change", function(){ state[k] = el.value; render(); });
    });

    document.getElementById("gear").addEventListener("click", function(){
      document.getElementById("panel").classList.toggle("open");
    });

    var gap = document.getElementById("gapjump");
    if (gap) gap.addEventListener("click", function(){
      document.getElementById("panel").classList.add("open");
      document.getElementById("named-not-linked").scrollIntoView({block:"start"});
    });

    document.getElementById("traycopy").addEventListener("click", function(){
      copy(playlistText(), this, "Copied", "Copy listening list");
    });
    document.getElementById("trayembed").addEventListener("click", function(){
      copy(embedHtml(), this, "Copied", "Copy Canvas embed");
    });
    document.getElementById("trayclear").addEventListener("click", function(){
      playlist = [];
      save();
      renderTray();
      render();
    });

    // Event delegation: the grid is replaced wholesale on every render, so a listener
    // bound to a button inside it would be thrown away with it.
    document.getElementById("grid").addEventListener("click", function(ev){
      var play = ev.target.closest(".playbtn");
      if (play){
        var v = byId(play.dataset.play);
        if (!v) return;
        var frame = play.parentNode;
        frame.innerHTML = '<iframe src="' + esc(v.embed_url) +
          '?rel=0&autoplay=1" title="' + esc(v.title || "") +
          '" allow="autoplay; encrypted-media; picture-in-picture" ' +
          'allowfullscreen></iframe>';
        return;
      }
      var add = ev.target.closest(".addbtn");
      if (add){
        var id = add.dataset.add;
        var at = playlist.indexOf(id);
        if (at > -1) playlist.splice(at, 1); else playlist.push(id);
        save();
        var inNow = playlist.indexOf(id) > -1;
        add.classList.toggle("in", inNow);
        add.textContent = inNow ? "In playlist" : "Add to playlist";
        renderTray();
        return;
      }
      var b = ev.target.closest(".copybtn");
      if (b) copy(b.dataset.url, b, "Copied", "Copy link");
    });
  }

  function restore(){
    try {
      var saved = JSON.parse(localStorage.getItem(STORE) || "{}");
      var st = saved.state || {};
      Object.keys(state).forEach(function(k){
        if (typeof st[k] === "string") state[k] = st[k];
      });
      if (Array.isArray(saved.playlist))
        // drop ids that no longer exist rather than rendering a phantom count
        playlist = saved.playlist.filter(function(id){ return !!byId(id); });
    } catch(e){}
    var q = document.getElementById("q");
    if (q) q.value = state.q;
    ["topic","sort"].forEach(function(k){
      var el = document.getElementById(k);
      // a saved value whose option no longer exists must not silently filter to nothing
      if (el && !Array.prototype.some.call(el.options,
            function(o){ return o.value === state[k]; })) state[k] = "";
      if (el) el.value = state[k];
    });
    // same for the chip axes: a restored course or genre that no longer has a chip
    // would filter the shelf to nothing with no visible control to clear
    [["course","[data-course]"],["genre","[data-genre]"]].forEach(function(pair){
      if (!state[pair[0]]) return;
      var found = false;
      document.querySelectorAll(pair[1]).forEach(function(c){
        if (c.dataset[pair[0]] === state[pair[0]]) found = true; });
      if (!found) state[pair[0]] = "";
    });
  }

  restore();
  wire();
  renderTray();
  render();
})();
"""
