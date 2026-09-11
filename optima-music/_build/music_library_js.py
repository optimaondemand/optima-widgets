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

  var state = {q:"", status:"", course:"", genre:"", kind:"", topic:"", xref:"",
               sort:"default"};
  var playlist = [];   // video ids the teacher has picked, in pick order
  var clips = {};      // video id -> {s, e} in seconds: the excerpt a teacher chose

  var CMAP = {};
  MUSIC.courses.forEach(function(c){ CMAP[c.id] = c; });
  var GENRE_LABEL = (MUSIC.labels || {})["music.genre"] || {};
  var KIND_LABEL = (MUSIC.labels || {})["video.kind"] || {};

  function norm(s){
    return (s||"").toString().toLowerCase()
      .normalize("NFD").replace(/[\\u0300-\\u036f]/g,"");
  }

  function esc(s){
    return (s == null ? "" : String(s))
      .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
      .replace(/"/g,"&quot;");
  }

  // ---- clip ranges. YouTube's player honours start= and end= on an embed and t= on a
  // watch link, so a teacher can point a class at the two minutes that matter without
  // re-hosting anything. Times are typed as m:ss and stored as seconds.
  function fmt(sec){
    sec = Math.max(0, Math.round(sec || 0));
    var h = Math.floor(sec / 3600), m = Math.floor((sec % 3600) / 60), s = sec % 60;
    var ms = (m < 10 && h ? "0" : "") + m + ":" + (s < 10 ? "0" : "") + s;
    return h ? h + ":" + ms : ms;
  }
  function parseTime(str){
    // "1:20", "80", "1:02:03" -> seconds. null for blank, NaN for not a time.
    var t = (str || "").replace(/\\s+/g, "");
    if (!t) return null;
    if (/^\\d+$/.test(t)) return parseInt(t, 10);
    var m = /^(\\d+):([0-5]?\\d)(?::([0-5]?\\d))?$/.exec(t);
    if (!m) return NaN;
    return m[3] != null ? (+m[1]) * 3600 + (+m[2]) * 60 + (+m[3])
                        : (+m[1]) * 60 + (+m[2]);
  }
  function clipFor(id){
    var c = clips[id];
    return (c && (c.s || c.e)) ? c : null;
  }
  function clipQuery(id){
    var c = clipFor(id), q = [];
    if (c && c.s) q.push("start=" + c.s);
    if (c && c.e) q.push("end=" + c.e);
    return q.join("&");
  }
  function clipLabel(id){
    var c = clipFor(id), v = byId(id);
    if (!c) return "";
    return fmt(c.s || 0) + "\u2013" +
      (c.e ? fmt(c.e) : (v && v.duration ? fmt(v.duration) : "end"));
  }
  function watchUrl(v){
    var c = clipFor(v.id);
    return v.url + (c && c.s ? "&t=" + c.s : "");
  }
  function clipRowFor(v){
    if (v.state !== "ok") return "";
    var c = clipFor(v.id) || {};
    var dur = v.duration ? fmt(v.duration) : "";
    return '<div class="cliprow" data-cliprow="' + esc(v.id) + '"' +
      (clipFor(v.id) ? "" : " hidden") + '>' +
      '<label>Play from <input type="text" inputmode="numeric" class="clipin" ' +
        'data-clip-start="' + esc(v.id) + '" value="' + (c.s ? fmt(c.s) : "") + '" ' +
        'placeholder="0:00" size="6"></label>' +
      '<label>to <input type="text" inputmode="numeric" class="clipin" ' +
        'data-clip-end="' + esc(v.id) + '" value="' + (c.e ? fmt(c.e) : "") + '" ' +
        'placeholder="' + esc(dur || "end") + '" size="6"></label>' +
      (dur ? '<span class="cliplen">of ' + esc(dur) + '</span>' : "") +
      '<button type="button" class="clipclear" data-clipclear="' + esc(v.id) + '"' +
        (clipFor(v.id) ? "" : " hidden") + '>Clear</button>' +
      '<span class="cliperr" data-cliperr="' + esc(v.id) + '"></span>' +
      '</div>';
  }
  function setClip(id, sIn, eIn){
    // returns an error string, or "" when the clip was stored (or cleared)
    var v = byId(id);
    var s = parseTime(sIn), e = parseTime(eIn);
    if (isNaN(s) || isNaN(e)) return "Type a time as minutes:seconds, like 1:20.";
    if (v && v.duration){
      if (s != null && s >= v.duration) return "The video ends at " + fmt(v.duration) + ".";
      if (e != null && e > v.duration) return "The video ends at " + fmt(v.duration) + ".";
    }
    if (s != null && e != null && e <= s) return "The end has to come after the start.";
    if (!s && !e) delete clips[id]; else clips[id] = {s: s || 0, e: e || 0};
    save();
    return "";
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
    v._kinds = (v.tags||[]).filter(function(t){ return t.scheme === "video.kind"; })
                           .map(function(t){ return t.code; });
    v._uses = (v.lessons||[]).length;
    v._art = ((v.cross_refs||{}).art||[]).length;
    v._ela = ((v.cross_refs||{}).ela||[]).length;
  });

  var DEFAULTS = {q:"", status:"", course:"", genre:"", kind:"", topic:"", xref:"",
                  sort:"default"};

  function activeCount(){
    return Object.keys(DEFAULTS).filter(function(k){
      return state[k] !== DEFAULTS[k]; }).length;
  }

  function clearAll(){
    // Back to everything: state, the search box, the selects and the stored copy. The
    // stored copy matters most -- filters persist across reloads, which is what made a
    // chosen filter feel permanent rather than merely sticky.
    Object.keys(DEFAULTS).forEach(function(k){ state[k] = DEFAULTS[k]; });
    var q = document.getElementById("q");
    if (q) q.value = "";
    ["topic","sort"].forEach(function(k){
      var el = document.getElementById(k);
      if (el) el.value = DEFAULTS[k];
    });
    // No removeItem here: render() ends in save(), which would write the key straight
    // back. Persisting the CLEARED state is the behaviour we want anyway -- it is what
    // makes "show everything" survive a reload, which is the half of this that was
    // broken. The picked listening list is deliberately untouched; it is not a filter.
    render();
  }

  function matches(v){
    if (state.q && v._hay.indexOf(norm(state.q)) === -1) return false;
    if (state.status && v.disposition !== state.status) return false;
    if (state.course && (v.courses||[]).indexOf(state.course) === -1) return false;
    if (state.genre && v._genres.indexOf(state.genre) === -1) return false;
    if (state.kind && v._kinds.indexOf(state.kind) === -1) return false;
    if (state.topic && v._topics.indexOf(state.topic) === -1) return false;
    if (state.xref === "art" && !v._art) return false;
    if (state.xref === "ela" && !v._ela) return false;
    return true;
  }

  function frameFor(v){
    if (v.state !== "ok"){
      var why = "No link on YouTube";
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

  function datesFor(v){
    // The upload date is not the interesting number: Beethoven's Ninth is 1824 whoever
    // posted it in 2019. work_year is the piece; recording_year only appears where this
    // performance is itself a separate datable event.
    if (!v.work_year && !v.recording_year) return "";
    var bits = [];
    if (v.work_year) bits.push("Work <b>" + esc(v.work_year) + "</b>");
    if (v.recording_year) bits.push("this recording <b>" + esc(v.recording_year) + "</b>");
    return '<p class="dates">' + bits.join(" &middot; ") + '</p>';
  }

  function noteFor(v){
    // Say what the piece is, but not when the note only repeats the title back.
    var note = v.piece_note;
    if (!note) return "";
    var worth = v.state !== "ok" || v.work_year || v.recording_year || note.length > 34;
    if (!worth) return "";
    return '<p class="pnote">' + esc(note) + '</p>';
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

  function prevFor(v){
    var ps = v.previous_lessons || [];
    if (!ps.length) return "";
    // Only worth showing where no rebuilt lesson cites the video: for anything currently
    // taught, where it USED to sit is history nobody needs on the card.
    if ((v.lessons || []).length) return "";
    return '<details class="uses prev"><summary>Previously in ' + ps.length +
      (ps.length === 1 ? " lesson" : " lessons") + '</summary><ul>' +
      ps.map(function(p){
        var c = CMAP[p.course];
        return '<li>' + esc(c ? c.short : p.course) +
          (p.module == null ? "" : " &middot; Module " + esc(p.module)) +
          (p.lesson_title ? ' &middot; ' + esc(p.lesson_title) : "") + '</li>';
      }).join("") + '</ul></details>';
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
    // lesson.topic labels are entire lesson titles ("Instruments of the Orchestra, The
    // Strings III-The Violoncello and The Double Bass") and wreck the pill row. They are
    // in the citation list instead, where the length belongs.
    var shown = (v.tags||[]).filter(function(t){ return t.scheme !== "lesson.topic"; });
    if (!shown.length) return "";
    return '<div class="pills">' + shown.map(function(t){
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
      h += '<p class="warn">No link on YouTube' +
           (v.state === "deleted" ? " — the channel deleted it"
            : v.state === "private" ? " — it was made private" : "") +
           '. The entry is kept for the record.</p>';
    h += datesFor(v);
    h += noteFor(v);
    h += courseBadges(v);
    if (v.attribution === "legacy-pool")
      h += '<p class="ch"><em>In the old exports of ' +
           esc((v.legacy_in||[]).map(function(id){
             return CMAP[id] ? CMAP[id].short : id; }).join(", ")) +
           ', but in no rebuilt module</em></p>';
    h += usesFor(v);
    h += prevFor(v);
    h += pillsFor(v);
    h += xrefFor(v);
    h += '<div class="foot">';
    h += '<a class="watch" href="' + esc(watchUrl(v)) + '" target="_blank" rel="noopener">' +
         (v.state === "ok" ? "Open on YouTube" : "Check the link") + '</a>';
    h += '<button class="copybtn" data-copy="' + esc(v.id) + '">Copy link</button>';
    if (v.state === "ok")
      h += '<button class="clipbtn' + (clipFor(v.id) ? ' set' : '') + '" data-clipbtn="' +
           esc(v.id) + '">' + (clipFor(v.id) ? 'Clip ' + esc(clipLabel(v.id)) : 'Set a clip') +
           '</button>';
    h += '<button class="addbtn' + (playlist.indexOf(v.id) > -1 ? ' in' : '') +
         '" data-add="' + esc(v.id) + '">' +
         (playlist.indexOf(v.id) > -1 ? 'In playlist' : 'Add to playlist') + '</button>';
    h += '</div>' + clipRowFor(v) + '</div></article>';
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
    var rank = {"in-use":1, "live-canvas":2, "previous-version":3, "unknown":4,
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
      lines.push("   Link:    " + watchUrl(v));
      if (v.duration) lines.push("   Length:  " + fmt(v.duration));
      if (clipFor(v.id)) lines.push("   Clip:    " + clipLabel(v.id));
      if ((v.courses||[]).length)
        lines.push("   Used in: " + v.courses.map(function(c){
          return CMAP[c] ? CMAP[c].name : c; }).join("; "));
      if (v.work_year) lines.push("   Work:    " + v.work_year +
        (v.recording_year ? "  (this recording " + v.recording_year + ")" : ""));
      if (v.piece_note) lines.push("   About:   " + v.piece_note);
      if ((v.tags||[]).length)
        lines.push("   Topics:  " + v.tags.filter(function(t){
          return t.scheme !== "lesson.topic"; }).map(function(t){return t.label;}).join(", "));
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
      var q = clipQuery(id);
      out.push('<p style="margin:22px 0 6px;font-family:Arial,Helvetica,sans-serif;' +
        'font-weight:bold;color:#0f2340;">' + esc(v.title || "") +
        (q ? ' <span style="font-weight:normal;color:#6b7a8d;">(' + esc(clipLabel(id)) +
             ')</span>' : '') + '</p>');
      // rel=0 keeps the end screen to this channel's own videos rather than whatever
      // YouTube would otherwise suggest to a student
      out.push('<iframe width="640" height="360" src="' + esc(v.embed_url) + '?rel=0' +
        (q ? '&' + q : '') +
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
    if (state.kind) shelf.push(KIND_LABEL[state.kind] || state.kind);
    var active = activeCount();
    var rb = document.getElementById("reset");
    if (rb) rb.hidden = active === 0;
    document.getElementById("resultline").innerHTML =
      (shelf.length ? "<b>" + shelf.map(esc).join(" &middot; ") + "</b> &mdash; " : "") +
      "showing <b>" + rows.length + "</b> of " + MUSIC.videos.length + " videos" +
      (state.course && state.sort === "default" ? ", in module order" : "") +
      (dead ? " &middot; <b>" + dead + "</b> with a link that no longer works" : "") +
      (active ? ' <button type="button" class="clear" id="clearinline">Show all ' +
                MUSIC.videos.length + ' videos</button>' : "");
    [["data-status","status"],["data-course","course"],["data-genre","genre"],
     ["data-kind","kind"],["data-xref","xref"]].forEach(function(pair){
      document.querySelectorAll("[" + pair[0] + "]").forEach(function(c){
        c.setAttribute("aria-pressed",
          String(c.dataset[pair[1]] === state[pair[1]] && state[pair[1]] !== ""));
      });
    });
    save();
  }

  function save(){
    try {
      localStorage.setItem(STORE, JSON.stringify({state: state, playlist: playlist,
                                                  clips: clips}));
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

    document.querySelectorAll("[data-kind]").forEach(function(c){
      c.addEventListener("click", function(){
        state.kind = (state.kind === c.dataset.kind) ? "" : c.dataset.kind;
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

    var rb = document.getElementById("reset");
    if (rb) rb.addEventListener("click", clearAll);

    // the inline link is inside the result line, which is rewritten on every render
    document.getElementById("resultline").addEventListener("click", function(ev){
      if (ev.target.closest("#clearinline")) clearAll();
    });

    // Escape clears, from anywhere including the search box
    document.addEventListener("keydown", function(ev){
      if (ev.key !== "Escape") return;
      if (activeCount()) { clearAll(); ev.preventDefault(); }
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
        var cq = clipQuery(v.id);
        frame.innerHTML = '<iframe src="' + esc(v.embed_url) +
          '?rel=0&autoplay=1' + (cq ? '&' + cq : '') + '" title="' + esc(v.title || "") +
          '" allow="autoplay; encrypted-media; picture-in-picture" ' +
          'allowfullscreen></iframe>';
        // Whether an embed plays is YouTube's call, not ours: a channel can disallow
        // embedding, and some origins are refused outright. When that happens the frame
        // says "Video unavailable" and the reader needs somewhere to go that is not the
        // back button.
        var out = document.createElement("p");
        out.className = "fallback";
        out.innerHTML = 'Not playing? <a href="' + esc(v.url) +
          '" target="_blank" rel="noopener">Watch it on YouTube</a>';
        if (frame.parentNode) frame.parentNode.insertBefore(out, frame.nextSibling);
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
      if (b){
        var cv = byId(b.dataset.copy);
        if (cv) copy(watchUrl(cv), b, "Copied", "Copy link");
        return;
      }
      var cb = ev.target.closest(".clipbtn");
      if (cb){
        var row = document.querySelector('[data-cliprow="' + cb.dataset.clipbtn + '"]');
        if (!row) return;
        row.hidden = !row.hidden;
        if (!row.hidden){ var first = row.querySelector("input"); if (first) first.focus(); }
        return;
      }
      var cc = ev.target.closest(".clipclear");
      if (cc){
        var cid = cc.dataset.clipclear;
        delete clips[cid];
        save();
        var crow = document.querySelector('[data-cliprow="' + cid + '"]');
        if (crow){
          crow.querySelectorAll("input").forEach(function(i){ i.value = ""; });
          crow.querySelector(".cliperr").textContent = "";
          cc.hidden = true;
        }
        reflectClip(cid);
      }
    });

    // A clip is stored when a time field is committed. change bubbles, so one listener
    // on the grid survives every re-render, the same as the click handler above.
    document.getElementById("grid").addEventListener("change", function(ev){
      var inp = ev.target.closest(".clipin");
      if (!inp) return;
      var id = inp.dataset.clipStart || inp.dataset.clipEnd;
      var row = document.querySelector('[data-cliprow="' + id + '"]');
      if (!row) return;
      var sIn = row.querySelector("[data-clip-start]"), eIn = row.querySelector("[data-clip-end]");
      var err = setClip(id, sIn.value, eIn.value);
      row.querySelector(".cliperr").textContent = err;
      if (!err){
        var c = clipFor(id);
        sIn.value = c && c.s ? fmt(c.s) : "";
        eIn.value = c && c.e ? fmt(c.e) : "";
      }
      row.querySelector(".clipclear").hidden = !clipFor(id);
      reflectClip(id);
    });
  }

  function reflectClip(id){
    // Everything on the card that carries the clip: the button label, the watch link,
    // and a player that is already open, which reloads at the new range.
    var v = byId(id);
    if (!v) return;
    var btn = document.querySelector('[data-clipbtn="' + id + '"]');
    if (btn){
      btn.classList.toggle("set", !!clipFor(id));
      btn.textContent = clipFor(id) ? "Clip " + clipLabel(id) : "Set a clip";
    }
    var card = document.querySelector('.card[data-id="' + id + '"]');
    if (card){
      var w = card.querySelector(".watch");
      if (w) w.href = watchUrl(v);
      var fr = card.querySelector(".frame iframe");
      if (fr){
        var cq = clipQuery(id);
        fr.src = v.embed_url + "?rel=0&autoplay=1" + (cq ? "&" + cq : "");
      }
    }
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
      if (saved.clips && typeof saved.clips === "object")
        Object.keys(saved.clips).forEach(function(id){
          var c = saved.clips[id];
          if (byId(id) && c && (typeof c.s === "number" || typeof c.e === "number"))
            clips[id] = {s: c.s > 0 ? c.s : 0, e: c.e > 0 ? c.e : 0};
        });
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
    [["course","[data-course]"],["genre","[data-genre]"],
     ["kind","[data-kind]"]].forEach(function(pair){
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
