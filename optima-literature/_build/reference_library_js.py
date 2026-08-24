# -*- coding: utf-8 -*-
"""
reference_library_js.py — behaviour for the ELA Reference Library.

Five named views over one dataset — three for teachers (All titles, Buy vs
free, Cost by grade) and two data-audit views behind the gear (Three lists,
Needs attention) — plus one-click list building from any of them.

NOTE ON .closest(): the Independent Reading pages once used tabs.closest('div'),
which returns the element ITSELF and silently broke every genre panel. Nothing
here calls .closest() on a container; element references are held directly and
row identity travels in data- attributes. build_reference_library.py gates on it.
"""

JS = """
(function(){
  var DATA = window.__LIB__ || [];
  var grid = document.getElementById('grid');
  var viewsEl = document.getElementById('views');
  var q = document.getElementById('q');
  var selGrade = document.getElementById('fGrade');
  var selShelf = document.getElementById('fShelf');
  var selState = document.getElementById('fState');
  var selTaught = document.getElementById('fTaught');
  var sortBtns = document.querySelectorAll('.sortbtn');
  var viewTabs = document.querySelectorAll('.vtab');
  var countEl = document.getElementById('count');
  var fab = document.getElementById('fab');
  var fabN = document.getElementById('fabN');
  var panel = document.getElementById('panel');
  var listBox = document.getElementById('listBox');

  var LS = 'optima-ela-ref-picks';
  var picked = {};
  try { picked = JSON.parse(localStorage.getItem(LS) || '{}') || {}; } catch(e){ picked = {}; }

  var sortMode = 'az';
  var view = 'library';
  var cards = [];            // {el, rec} for the card grid
  var byId = {};             // id -> rec

  var DASH = '—';   // real em dash, never the entity: esc() would eat it
  var STATE_LABEL = {identical:'Free', similar:'Similar', none:'Buy'};

  // Friendly name for a free-text host. Naming the SOURCE is more useful than
  // repeating the status word already shown on the pill.
  var SRC = {
    'gutenberg':'Project Gutenberg', 'gutenberg.org':'Project Gutenberg',
    'gutenberg.net.au':'Gutenberg Australia', 'gutenberg.ca':'Gutenberg Canada',
    'en.wikisource.org':'Wikisource', 'wikisource.org':'Wikisource',
    'standardebooks.org':'Standard Ebooks',
    'guides.loc.gov':'Library of Congress', 'loc.gov':'Library of Congress',
    'folger.edu':'Folger', 'americanenglish.state.gov':'American English (US State Dept)',
    'fordlibrarymuseum.gov':'Ford Presidential Library',
    'americanliterature.com':'American Literature', 'archive.org':'Internet Archive'
  };
  function sourceName(h){ return SRC[h] || h; }
  // Brand palette (Optima guidelines v2.0) — keep in sync with the Python
  // STATE_COLOR / FLAG_COLOR in build_reference_library.py.
  var STATE_COLOR = {identical:'#4B7F20', similar:'#0E5568', none:'#B85F00'};
  var FLAG_COLOR  = {archaic:'#8F347F', older:'#51617C'};

  function esc(s){
    return String(s == null ? '' : s)
      .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
      .replace(/"/g,'&quot;');
  }
  function nPicked(){ var n=0; for (var k in picked){ if(picked[k]) n++; } return n; }
  function savePicks(){ try{ localStorage.setItem(LS, JSON.stringify(picked)); }catch(e){} }
  function statePill(s){
    return '<span class="pill" style="--bc:'+STATE_COLOR[s]+'">'+STATE_LABEL[s]+'</span>';
  }

  function matches(rec){
    if (selGrade.value && rec.grade !== selGrade.value) return false;
    if (selShelf.value && rec.shelfSlug !== selShelf.value) return false;
    if (selState.value && rec.state !== selState.value) return false;
    if (selTaught.value && rec.taught !== selTaught.value) return false;
    var s = (q.value || '').trim().toLowerCase();
    if (s && rec.k.indexOf(s) === -1) return false;
    return true;
  }
  function filtered(){
    var out = [];
    for (var i=0;i<DATA.length;i++){ if (matches(DATA[i])) out.push(DATA[i]); }
    return out;
  }

  function cmp(a, b){
    if (sortMode === 'grade'){
      if (a.gradeNum !== b.gradeNum) return a.gradeNum - b.gradeNum;
      return a.sortTitle < b.sortTitle ? -1 : 1;
    }
    if (sortMode === 'author'){
      if (a.authorKey !== b.authorKey) return a.authorKey < b.authorKey ? -1 : 1;
      return a.sortTitle < b.sortTitle ? -1 : 1;
    }
    if (sortMode === 'shelf'){
      if (a.shelf !== b.shelf) return a.shelf < b.shelf ? -1 : 1;
      return a.sortTitle < b.sortTitle ? -1 : 1;
    }
    return a.sortTitle < b.sortTitle ? -1 : 1;
  }
  function headingFor(rec){
    if (sortMode === 'grade') return 'Grade ' + rec.grade;
    if (sortMode === 'shelf') return rec.shelf;
    if (sortMode === 'author') return (rec.authorDisplay || 'Unattributed');
    var c = rec.sortTitle.charAt(0).toUpperCase();
    return /[A-Z]/.test(c) ? c : '#';
  }

  /* ---------------- selection ---------------- */

  function setPicked(id, on){
    if (on) picked[id] = true; else delete picked[id];
  }
  function syncCardChrome(){
    for (var i=0;i<cards.length;i++){
      var on = !!picked[cards[i].rec.id];
      var cb = cards[i].el.querySelector('.cb');
      if (cb) cb.checked = on;
      cards[i].el.className = on ? 'book sel' : 'book';
    }
  }
  function refreshFab(){
    var n = nPicked();
    fabN.textContent = n;
    fab.style.display = n ? 'block' : 'none';
  }

  /* ---------------- the card grid ---------------- */

  function drawLibrary(){
    viewsEl.hidden = true;
    grid.style.display = '';
    var vis = filtered().slice().sort(cmp);
    var want = {};
    for (var i=0;i<vis.length;i++) want[vis[i].id] = i;

    while (grid.firstChild) grid.removeChild(grid.firstChild);
    if (!vis.length){
      var n = document.createElement('div');
      n.className = 'noresult';
      n.textContent = 'No titles match those filters.';
      grid.appendChild(n);
    } else {
      var lastHead = null;
      for (var j=0;j<vis.length;j++){
        var h = headingFor(vis[j]);
        if (h !== lastHead){
          var hd = document.createElement('div');
          hd.className = 'secthead';
          hd.appendChild(document.createTextNode(h));
          grid.appendChild(hd);
          lastHead = h;
        }
        var c = cardFor(vis[j].id);
        if (c) grid.appendChild(c);
      }
    }
    countEl.textContent = vis.length + ' of ' + DATA.length + ' titles';
  }
  var cardIndex = {};
  function cardFor(id){ return cardIndex[id] || null; }

  /* ---------------- table views ---------------- */

  function tickBtn(id){
    var on = !!picked[id];
    return '<button class="tick" data-tick="'+esc(id)+'">'
      + (on ? '&#10003; on list' : '+ add') + '</button>';
  }
  function shell(title, lede, body){
    return '<h2 class="vhead">'+title+'</h2><div class="vlede">'+lede+'</div>'+body;
  }
  function table(head, rows, empty){
    if (!rows.length) return '<div class="noresult">'+(empty||'Nothing here.')+'</div>';
    return '<div class="tw"><table class="vt"><thead><tr>'+head+'</tr></thead><tbody>'
      + rows.join('') + '</tbody></table></div>';
  }

  function viewCompare(){
    var rows = filtered().filter(function(r){ return r.freeUrl; }).sort(cmp);
    var out = rows.map(function(r){
      var same = r.state === 'identical';
      return '<tr'+(same?'':' class="diff"')+'>'
        + '<td class="t">'+esc(r.title)+'<br><span style="font-weight:400;color:#6b7a99;font-size:11.5px;">'
          + esc(r.authorDisplay)+'</span></td>'
        + '<td class="m">'+esc(r.grade)+'</td>'
        + '<td class="m">'+(r.translator || r.listedEdition ? esc(r.translator || r.listedEdition) : DASH)
          + (r.isbn ? '<br>ISBN '+esc(r.isbn) : '')
          + (r.buyUrl ? '<br><a href="'+esc(r.buyUrl)+'" target="_blank" rel="noopener">purchase</a>' : '')
          + '</td>'
        + '<td class="m">'+(r.freeSource ? esc(sourceName(r.freeSource)) : DASH)
          + (r.freeMatchedTitle ? '<br>'+esc(r.freeMatchedTitle) : '')
          + '<br><a href="'+esc(r.freeUrl)+'" target="_blank" rel="noopener">read free</a></td>'
        + '<td>'+(same
            ? '<span class="agree">same text</span>'
            : '<span class="clash">different version</span>')+'</td>'
        + '<td>'+tickBtn(r.id)+'</td></tr>';
    });
    return shell('Buy versus free',
      'Only titles where a free version exists. Rows shaded pink are a <b>different '
      + 'translation or edition</b> from the one the book list names &mdash; fine to hand a '
      + 'student who cannot buy the book, but do not assign by page or line across two versions.',
      table('<th>Title</th><th>Gr</th><th>Listed edition</th><th>Free version</th>'
            + '<th>Match</th><th></th>', out,
            'No free versions among the current filters.'));
  }

  function viewGrades(){
    var rows = filtered();
    var g = {};
    for (var i=0;i<rows.length;i++){
      var r = rows[i];
      if (!g[r.grade]) g[r.grade] = {free:0, sim:0, buy:0, n:0, num:r.gradeNum};
      g[r.grade].n++;
      if (r.state === 'identical') g[r.grade].free++;
      else if (r.state === 'similar') g[r.grade].sim++;
      else g[r.grade].buy++;
    }
    var keys = Object.keys(g).sort(function(a,b){ return g[a].num - g[b].num; });
    var out = keys.map(function(k){
      var d = g[k], pct = function(x){ return d.n ? (100*x/d.n).toFixed(1) : 0; };
      return '<tr>'
        + '<td class="t">Grade '+esc(k)+'</td>'
        + '<td class="n">'+d.n+'</td>'
        + '<td class="n" style="color:#4B7F20;font-weight:600;">'+d.free+'</td>'
        + '<td class="n" style="color:#0E5568;font-weight:600;">'+d.sim+'</td>'
        + '<td class="n" style="color:#B85F00;font-weight:600;">'+d.buy+'</td>'
        + '<td><div class="bar">'
          + '<i style="background:#4B7F20;width:'+pct(d.free)+'%"></i>'
          + '<i style="background:#0E5568;width:'+pct(d.sim)+'%"></i>'
          + '<i style="background:#B85F00;width:'+pct(d.buy)+'%"></i>'
          + '</div></td>'
        + '<td><button class="tick" data-gradebuy="'+esc(k)+'">list what to buy</button></td>'
        + '</tr>';
    });
    return shell('What each grade costs',
      'Counts respect the filters above. <b>Free</b> means the public-domain text is the '
      + 'same text; <b>similar</b> means a free version exists in another edition; '
      + '<b>buy</b> means students need a licensed copy. The last column builds that '
      + "grade's purchase list in one click.",
      table('<th>Grade</th><th class="n">Titles</th><th class="n">Free</th>'
            + '<th class="n">Similar</th><th class="n">Buy</th><th>Mix</th><th></th>',
            out, 'Nothing matches the current filters.'));
  }

  function viewSources(){
    var REV = {PD:'public domain', COPYRIGHT:'in copyright',
               PD_WORK_C_EDITION:'PD work, © edition', MIXED:'mixed',
               UNCLEAR:'unclear'};
    var rows = filtered().slice().sort(cmp);
    var out = rows.map(function(r){
      var rev = r.reviewCategory ? (REV[r.reviewCategory] || r.reviewCategory) : '&mdash;';
      // A clash worth showing: the sheet says PD but the taught edition is a
      // copyrighted translation, or the sheet says © but our state says free.
      var clash = '';
      if (r.reviewCategory === 'PD' && r.state === 'none') clash = 'sheet says PD, no free source';
      else if (r.reviewCategory === 'COPYRIGHT' && r.state !== 'none') clash = 'sheet says ©, free text exists';
      else if (r.reviewCategory === 'PD' && r.taughtEdition &&
               /1951|1953|Coghill|Watling|Heaney|Fitzgerald|Fitts/i.test(r.taughtEdition))
        clash = 'sheet says PD, taught edition is ©';
      return '<tr'+(clash?' class="diff"':'')+'>'
        + '<td class="t">'+esc(r.title)+'</td>'
        + '<td class="m">'+esc(r.grade)+'</td>'
        + '<td class="m">'+(r.buyUrl ? 'listed' : '<span style="color:#a8afc0;">not listed</span>')
          + (r.listedEdition ? '<br>'+esc(r.listedEdition) : '')+'</td>'
        + '<td class="m">'+rev+'</td>'
        + '<td class="m">'+(r.taughtEdition ? esc(r.taughtEdition)
            : (r.taughtUse ? esc(r.taughtUse) : '<span style="color:#a8afc0;">not taught</span>'))+'</td>'
        + '<td>'+(clash ? '<span class="clash">'+clash+'</span>'
                        : '<span class="agree">consistent</span>')+'</td>'
        + '<td>'+tickBtn(r.id)+'</td></tr>';
    });
    return shell('The three lists, side by side',
      'The official book list says what a family may buy. The 2026-04-30 review sheet '
      + 'triaged rights by title. The taught column is what the coursework actually uses '
      + '&mdash; and rights live in the edition, so that column is the authoritative one. '
      + 'Shaded rows are where the three disagree.',
      table('<th>Title</th><th>Gr</th><th>Book list</th><th>Review sheet</th>'
            + '<th>Taught edition</th><th>Agreement</th><th></th>', out));
  }

  // The 'Translations by age' view was removed 2026-08-24 (Jessica: the
  // category earned no tab of its own). The Archaic/Older flags still render
  // on every card and in the key; the per-translation data stays in __LIB__.

  function viewAttention(){
    var rows = filtered().filter(function(r){
      return r.verify || r.freeReason === 'needs_sourcing' || r.storedFileOk === false;
    }).sort(cmp);
    var out = rows.map(function(r){
      var issues = [];
      if (r.verify) issues.push('<span class="pill" style="--bc:#67308F">verify</span>');
      if (r.freeReason === 'needs_sourcing')
        issues.push('<span class="pill" style="--bc:#51617C">no source</span>');
      if (r.storedFileOk === false)
        issues.push('<span class="pill" style="--bc:#8F347F">file</span>');
      return '<tr>'
        + '<td class="t">'+esc(r.title)+'</td>'
        + '<td class="m">'+esc(r.grade)+'</td>'
        + '<td>'+issues.join(' ')+'</td>'
        + '<td class="m">'+esc(r.verifyNote || r.freeReason || '')+'</td>'
        + '<td>'+tickBtn(r.id)+'</td></tr>';
    });
    return shell('Needs attention',
      'Three kinds of problem. <b>Verify</b> means a date or rights claim that cannot be '
      + 'checked from the coursework itself. <b>No source</b> means the work is public '
      + 'domain but no trusted free copy has been found. <b>File</b> means the copy in the '
      + 'course folder has something wrong with it. None of these blocks teaching; all of '
      + 'them are worth closing.',
      table('<th>Title</th><th>Gr</th><th>Issue</th><th>What is wrong</th><th></th>', out,
            'Nothing needs attention among the current filters.'));
  }

  var VIEWS = {compare:viewCompare, grades:viewGrades, sources:viewSources,
               attention:viewAttention};

  function drawView(){
    grid.style.display = 'none';
    viewsEl.hidden = false;
    viewsEl.innerHTML = VIEWS[view]();
    var n = viewsEl.querySelectorAll('table.vt tbody tr').length;
    countEl.textContent = n + ' row' + (n===1?'':'s');
    // wire the row buttons
    var ticks = viewsEl.querySelectorAll('[data-tick]');
    for (var i=0;i<ticks.length;i++){
      ticks[i].addEventListener('click', (function(btn){
        return function(){
          var id = btn.getAttribute('data-tick');
          setPicked(id, !picked[id]);
          btn.innerHTML = picked[id] ? '&#10003; on list' : '+ add';
          savePicks(); syncCardChrome(); refreshFab();
        };
      })(ticks[i]));
    }
    var gb = viewsEl.querySelectorAll('[data-gradebuy]');
    for (var j=0;j<gb.length;j++){
      gb[j].addEventListener('click', (function(btn){
        return function(){
          var g = btn.getAttribute('data-gradebuy');
          for (var k=0;k<DATA.length;k++){
            if (DATA[k].grade === g && DATA[k].state === 'none') setPicked(DATA[k].id, true);
          }
          savePicks(); syncCardChrome(); refreshFab(); openPanel();
        };
      })(gb[j]));
    }
  }

  function draw(){ if (view === 'library') drawLibrary(); else drawView(); }

  /* ---------------- my list ---------------- */

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
    var tg = rec.taughtEdition
      ? '<span class="m">Optima Gr '+esc(rec.taughtGrade)+' uses '+esc(rec.taughtEdition)+'</span>' : '';
    return '<div class="li"><b>' + esc(rec.title) + '</b>'
      + (rec.authorDisplay ? ' &mdash; ' + esc(rec.authorDisplay) : '')
      + (rec.firstPub ? ' <span class="m" style="display:inline">(' + esc(rec.firstPub) + ')</span>' : '')
      + m + tg + lk + '</div>';
  }

  function buildList(){
    var buy = [], sim = [], free = [];
    for (var i=0;i<DATA.length;i++){
      var r = DATA[i];
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
    // The pocket-card header. The date is stamped at open time, like a real
    // checkout card, and the Teacher / Class blanks are there to be filled in
    // by hand on the printed copy.
    var stamp = new Date().toLocaleDateString(undefined,
      {year:'numeric', month:'short', day:'2-digit'}).toUpperCase();
    var head = '<div class="cardhead">'
      + '<div class="ch-left">'
      + '<div class="ch-org">Optima Academy Online &middot; ELA Reference Library</div>'
      + '<div class="ch-title">Reading &amp; Purchase List</div>'
      + '</div>'
      + '<div class="ch-stamp">ISSUED &#9656; ' + esc(stamp) + '</div>'
      + '</div>'
      + '<div class="ch-meta"><span>Teacher</span><span class="blank"></span>'
      + '<span>Class</span><span class="blank"></span></div>'
      + '<div class="lede">' + total + ' title' + (total===1?'':'s')
      + ' selected. Students need to buy ' + buy.length
      + '; ' + (free.length + sim.length) + ' can be read free.</div>';
    var body = sec('', 'Students must purchase',
        'In copyright. A free PDF found online is not a licence.', buy)
      + sec('s', 'Free, but a different version',
        'The free text is a different translation or edition from the one the book list '
        + 'specifies. Fine for reference; do not assign by page or line across versions.', sim)
      + sec('f', 'Free, same text',
        'Public domain, and the free text is the assigned text.', free);
    if (!total) body = '<div class="empty">Nothing selected yet. Tick a card, or use '
      + '&ldquo;Make a list&hellip;&rdquo; in the toolbar.</div>';
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
      picked = {}; savePicks(); syncCardChrome(); refreshFab(); buildList(); draw();
    };
    document.getElementById('pCopy').onclick = function(){
      var txt = listBox.innerText.replace(/\\n{3,}/g, '\\n\\n');
      if (navigator.clipboard) navigator.clipboard.writeText(txt);
      var b = this; b.textContent = 'Copied';
      setTimeout(function(){ b.textContent = 'Copy as text'; }, 1400);
    };
  }

  function openPanel(){ buildList(); panel.className = 'panel open'; }
  function closePanel(){ panel.className = 'panel'; }

  /* ---------------- wiring ---------------- */

  var nodes = grid.querySelectorAll('.book');
  for (var i=0;i<nodes.length;i++){
    var el = nodes[i];
    var rec = DATA[parseInt(el.getAttribute('data-i'), 10)];
    if (!rec) continue;
    cards.push({el: el, rec: rec});
    cardIndex[rec.id] = el;
    byId[rec.id] = rec;
    var cb = el.querySelector('.cb');
    if (cb){
      cb.addEventListener('change', (function(el, rec, cb){
        return function(){
          setPicked(rec.id, cb.checked);
          el.className = cb.checked ? 'book sel' : 'book';
          savePicks(); refreshFab();
        };
      })(el, rec, cb));
    }
  }
  syncCardChrome();

  q.addEventListener('input', draw);
  selGrade.addEventListener('change', draw);
  selShelf.addEventListener('change', draw);
  selState.addEventListener('change', draw);
  selTaught.addEventListener('change', draw);
  for (var s=0;s<sortBtns.length;s++){
    sortBtns[s].addEventListener('click', (function(btn){
      return function(){
        sortMode = btn.getAttribute('data-sort');
        for (var t=0;t<sortBtns.length;t++)
          sortBtns[t].setAttribute('aria-pressed', sortBtns[t] === btn ? 'true' : 'false');
        draw();
      };
    })(sortBtns[s]));
  }
  for (var v=0;v<viewTabs.length;v++){
    viewTabs[v].addEventListener('click', (function(btn){
      return function(){
        view = btn.getAttribute('data-view');
        for (var t=0;t<viewTabs.length;t++)
          viewTabs[t].setAttribute('aria-pressed', viewTabs[t] === btn ? 'true' : 'false');
        draw();
        window.scrollTo({top: 0, behavior: 'smooth'});
      };
    })(viewTabs[v]));
  }

  // The gear shows/hides the two data-audit tabs (Three lists, Needs
  // attention). Closing it while an audit view is on screen returns to the
  // library, so the page never shows a view whose tab is hidden.
  var adminToggle = document.getElementById('adminToggle');
  var viewbar = document.getElementById('viewbar');
  adminToggle.addEventListener('click', function(){
    var open = viewbar.className.indexOf('show-admin') !== -1;
    if (open){
      viewbar.className = 'viewbar';
      adminToggle.setAttribute('aria-expanded', 'false');
      if (view === 'sources' || view === 'attention'){
        view = 'library';
        for (var t=0;t<viewTabs.length;t++)
          viewTabs[t].setAttribute('aria-pressed',
            viewTabs[t].getAttribute('data-view') === 'library' ? 'true' : 'false');
        draw();
      }
    } else {
      viewbar.className = 'viewbar show-admin';
      adminToggle.setAttribute('aria-expanded', 'true');
    }
  });
  fab.addEventListener('click', openPanel);
  panel.addEventListener('click', function(ev){ if (ev.target === panel) closePanel(); });
  document.addEventListener('keydown', function(ev){ if (ev.key === 'Escape') closePanel(); });

  // Reveal the controls only now that the script has run, so a JS failure leaves
  // the full linear card list visible rather than an empty page.
  //
  // REMOVE THE CLASS -- do not set style.display = ''. Clearing an inline style
  // just lets the stylesheet's .js-only{display:none} win again, which kept the
  // whole toolbar invisible. Removing the class lets each element fall back to
  // its own natural display (block for .controls, block for .viewbar).
  var jo = document.querySelectorAll('.js-only');
  for (var z=jo.length-1; z>=0; z--) jo[z].classList.remove('js-only');

  refreshFab();
  draw();
})();
"""
