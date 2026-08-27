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


  /* ---------------- teacher bookshelves ----------------

     Two views that share the catalogue with everything else on the page:
     My Classroom writes a shelf, Teacher Bookshelves reads every shelf.

     Published shelves arrive in window.__SHELVES__, built from classrooms.json.
     A teacher's own unsent work lives in localStorage and is labelled a draft,
     because a draft is visible to nobody else until the team commits it, and a
     shelf that looks published when it is not would be a lie to the teacher. */

  var SHELVES = window.__SHELVES__ || [];
  var YEAR = window.__SCHOOL_YEAR__ || '';
  var LSC = 'optima-ela-classroom';
  var GRADE_LIST = ['K','1','2','3','4','5','6','7','8','9','10','11','12'];

  var me = {teacher:'', subject:'ELA', grade:'11', level:'', course:'',
            delivery:'Live', period:'', courses:[]};
  try {
    var savedMe = JSON.parse(localStorage.getItem(LSC) || 'null');
    if (savedMe && typeof savedMe === 'object') {
      me = savedMe;
      if (!me.courses) me.courses = [];
    }
  } catch(e){}

  var tbPick = {};
  var tbScope = true;
  var tbEdit = -1;

  function saveMe(){ try{ localStorage.setItem(LSC, JSON.stringify(me)); }catch(e){} }

  var byIdMap = null;
  function recFor(id){
    if (!byIdMap){
      byIdMap = {};
      for (var i=0;i<DATA.length;i++) byIdMap[DATA[i].id] = DATA[i];
    }
    return byIdMap[id] || null;
  }

  function hostOf(url){
    var m = /^https?:[/][/]([^/]+)/.exec(url || '');
    return m ? m[1].toLowerCase().replace('www.','') : '';
  }
  var VENDOR = {'amazon.com':'Amazon', 'a.co':'Amazon', 'folger.edu':'Folger',
                'guides.loc.gov':'Library of Congress'};
  function vendorName(url){ var h = hostOf(url); return VENDOR[h] || h || 'purchase'; }

  function tbCount(n, word){
    countEl.textContent = n + ' ' + word + (n === 1 ? '' : 's');
  }

  /* ---- shared rendering ---- */

  function tbBadges(s){
    var lv = s.level === 'AP' ? '#B85F00' : (s.level === 'Honors' ? '#0E5568' : null);
    var h = '<span class="bdg" style="--bc:#8DA0B6">Grade ' + esc(s.grade) + '</span>';
    h += lv ? '<span class="bdg" style="--bc:'+lv+'">'+esc(s.level)+'</span>'
            : '<span class="bdg" style="--bc:#8DA0B6">Standard</span>';
    if (s.delivery === 'On-Demand'){
      h += '<span class="bdg" style="--bc:#0E5568">On-Demand</span>';
    } else {
      h += '<span class="bdg" style="--bc:#8DA0B6">'
         + (s.period ? 'Period ' + esc(s.period) : 'Live') + '</span>';
    }
    return h;
  }

  function tbEditionLine(r){
    var bits = [];
    if (r.translator)  bits.push('trans. ' + esc(r.translator));
    if (r.editor)      bits.push('ed. ' + esc(r.editor));
    if (r.publisher)   bits.push(esc(r.publisher));
    if (r.editionYear) bits.push(esc(r.editionYear));
    if (r.isbn)        bits.push('ISBN ' + esc(r.isbn));
    return bits.join(' ' + DASH + ' ');
  }

  function tbBook(r){
    if (!r) return '';
    var h = '<div class="tbbk"><div class="tbbktop">' + statePill(r.state)
          + '<span><span class="tbbkt">' + esc(r.title) + '</span> '
          + '<span class="tbbka">' + esc(r.authorDisplay || '') + '</span>';
    var ed = tbEditionLine(r);
    if (ed) h += '<div class="tbbked">' + ed + '</div>';
    h += '</span></div>';
    var acts = '';
    if (r.buyUrl){
      acts += '<a class="act buy" href="' + esc(r.buyUrl) + '" target="_blank" '
            + 'rel="noopener" data-plain="' + esc(tbPlainUrl(r.buyUrl)) + '" '
            + 'title="Buy the edition the book list names">'
            + esc(vendorName(r.buyUrl)) + '</a>';
    }
    if (r.freeUrl){
      acts += '<a class="act ' + (r.state === 'identical' ? 'free' : 'sim') + '" href="'
            + esc(r.freeUrl) + '" target="_blank" rel="noopener" data-plain="'
            + esc(tbPlainUrl(r.freeUrl)) + '">'
            + esc(sourceName(r.freeSource)) + '</a>';
    }
    if (r.readOnlineUrl){
      acts += '<a class="act ro" href="' + esc(r.readOnlineUrl) + '" target="_blank" '
            + 'rel="noopener" data-plain="' + esc(tbPlainUrl(r.readOnlineUrl)) + '" '
            + 'title="Read on the publisher site; not a download">'
            + esc(sourceName(hostOf(r.readOnlineUrl))) + '</a>';
    }
    h += acts ? '<div class="acts">' + acts + '</div>'
              : '<span class="tbnolink">No link on the catalogue entry.</span>';
    return h + '</div>';
  }

  function tbShelfCard(s, draft, idx){
    var ids = s.titles || [];
    var books = '';
    for (var i=0;i<ids.length;i++) books += tbBook(recFor(ids[i]));
    return '<div class="tbshelf"' + (draft ? ' style="border-top-color:#8DA0B6"' : '') + '>'
      + '<div class="tbsh"><div class="tbsteach">' + esc(s.teacher)
      + (draft ? ' <span class="bdg" style="--bc:#8F347F">Draft</span>' : '')
      + '</div><div class="tbscourse">' + esc(s.course) + '</div>'
      + '<div class="tbsmeta">' + tbBadges(s) + '</div>'
      + '<div class="tbprintonly">Optima Academy Online'
      + (YEAR ? ' &middot; ' + esc(YEAR) : '')
      + ' &middot; chosen from the approved ELA book list</div></div>'
      + '<div class="tbscount"><b>' + ids.length + '</b>'
      + '<span>titles from the approved catalogue</span></div>'
      + '<div class="tbsbooks">' + books + '</div>'
      + '<div class="tbsfoot">'
      + '<button class="tick" data-tbprint="' + idx + '">Print this shelf</button>'
      + '<button class="tick" data-tbcopy="' + idx + '">Copy book list</button>'
      + (draft ? '<span class="tbnolink">Visible only to you until your team '
               + 'publishes it.</span>' : '')
      + '</div></div>';
  }


  /* ---- clipboard and print ---- */

  var NL = String.fromCharCode(10);
  var tbRendered = [];

  function tbFlash(btn, msg){
    if (btn.getAttribute('data-busy')) return;
    var was = btn.textContent;
    btn.setAttribute('data-busy', '1');
    btn.textContent = msg;
    btn.className = btn.className + ' tbcopied';
    setTimeout(function(){
      btn.textContent = was;
      btn.className = btn.className.replace(' tbcopied', '');
      btn.removeAttribute('data-busy');
    }, 1700);
  }

  function tbToClipboard(text, btn){
    function fallback(){
      // execCommand is deprecated but still the only route on an insecure
      // origin, and a teacher opening the file locally is exactly that.
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly', '');
      ta.style.position = 'fixed';
      ta.style.top = '-2000px';
      document.body.appendChild(ta);
      ta.select();
      var done = false;
      try { done = document.execCommand('copy'); } catch(e){ done = false; }
      document.body.removeChild(ta);
      tbFlash(btn, done ? 'Copied' : 'Could not copy');
    }
    if (navigator.clipboard && navigator.clipboard.writeText){
      navigator.clipboard.writeText(text).then(
        function(){ tbFlash(btn, 'Copied'); }, fallback);
    } else { fallback(); }
  }


  function tbPlainUrl(u){
    if (!u) return '';
    // &amp; is decoded LAST: doing it first would turn &amp;lt; into a real <.
    return String(u)
      .split('&lt;').join('<')
      .split('&gt;').join('>')
      .split('&quot;').join('"')
      .split('&#39;').join(String.fromCharCode(39))
      .split('&amp;').join('&');
  }

  function tbWhereLine(s){
    var bits = ['Grade ' + s.grade];
    if (s.level) bits.push(s.level);
    bits.push(s.delivery === 'On-Demand'
      ? 'On-Demand' : (s.period ? 'Period ' + s.period : 'Live'));
    return bits.join(', ');
  }

  function tbEditionText(r){
    var bits = [];
    if (r.translator)  bits.push('trans. ' + r.translator);
    if (r.editor)      bits.push('ed. ' + r.editor);
    if (r.publisher)   bits.push(r.publisher);
    if (r.editionYear) bits.push(r.editionYear);
    if (r.isbn)        bits.push('ISBN ' + r.isbn);
    return bits.join(' - ');
  }

  function tbShelfText(s){
    var out = [];
    out.push(s.teacher + ' - ' + s.course + ' (' + tbWhereLine(s) + ')');
    out.push('Optima Academy Online' + (YEAR ? ' - ' + YEAR : ''));
    out.push('Titles chosen from the approved ELA book list.');
    out.push('');
    var ids = s.titles || [];
    var n = 0;
    for (var i=0;i<ids.length;i++){
      var r = recFor(ids[i]);
      if (!r) continue;
      n++;
      out.push(n + '. ' + r.title + (r.authorDisplay ? ' - ' + r.authorDisplay : ''));
      var ed = tbEditionText(r);
      if (ed) out.push('   ' + ed);
      if (r.state === 'identical') out.push('   Free: this exact text is public domain.');
      else if (r.state === 'similar') out.push('   A free version exists in a different edition.');
      else out.push('   Needs a purchased copy.');
      if (r.buyUrl) out.push('   Buy: ' + tbPlainUrl(r.buyUrl));
      if (r.freeUrl) out.push('   Free (' + sourceName(r.freeSource) + '): '
                              + tbPlainUrl(r.freeUrl));
      if (r.readOnlineUrl) out.push('   Read online: ' + tbPlainUrl(r.readOnlineUrl));
      out.push('');
    }
    if (!n) out.push('No titles chosen yet.');
    return out.join(NL);
  }

  function tbPrintShelf(idx){
    var cards = document.querySelectorAll('#tbShelfGrid .tbshelf');
    var el = cards[idx];
    if (!el) return;
    function cleanup(){
      document.body.className = document.body.className.replace(' tbprinting', '');
      el.className = el.className.replace(' tbprintme', '');
      if (window.onafterprint === cleanup) window.onafterprint = null;
    }
    el.className = el.className + ' tbprintme';
    document.body.className = document.body.className + ' tbprinting';
    window.onafterprint = cleanup;
    try { window.print(); } catch(e){}
    setTimeout(cleanup, 500);
  }

  /* ---- view: My Classroom ---- */

  function tbCatalogue(){
    var s = (document.getElementById('tbSearch') || {}).value || '';
    s = s.trim().toLowerCase();
    var out = [];
    for (var i=0;i<DATA.length;i++){
      var r = DATA[i];
      if (tbScope && !s && r.grade !== me.grade) continue;
      if (s && r.k.indexOf(s) === -1) continue;
      out.push(r);
    }
    out.sort(function(a,b){ return a.sortTitle < b.sortTitle ? -1 : 1; });
    return out;
  }

  function tbNPick(){ var n=0; for (var k in tbPick){ if (tbPick[k]) n++; } return n; }

  function tbSelect(id, label, value, opts){
    var h = '<div class="tbfield" id="' + id + 'Wrap"><label for="' + id + '">'
          + label + '</label><select id="' + id + '">';
    for (var i=0;i<opts.length;i++){
      var v = opts[i][0], t = opts[i][1];
      h += '<option value="' + esc(v) + '"' + (v === value ? ' selected' : '') + '>'
         + esc(t) + '</option>';
    }
    return h + '</select></div>';
  }

  function viewMine(){
    var grades = [];
    for (var g=0;g<GRADE_LIST.length;g++) grades.push([GRADE_LIST[g], 'Grade ' + GRADE_LIST[g]]);

    var form = '<div class="tbcard"><div class="tbhead"><span class="tbnum">1</span>'
      + '<span class="tbname">Your course</span>'
      + '<span class="tbnote">Every field stays editable</span></div>'
      + '<div class="tbbody"><div class="tbgrid">'
      + '<div class="tbfield"><label for="tbTeacher">Teacher name</label>'
      + '<input id="tbTeacher" type="text" value="' + esc(me.teacher)
      + '" placeholder="e.g. A. Rivera" /></div>'
      + tbSelect('tbSubject', 'Subject', me.subject, [['ELA','ELA'],['History','History']])
      + tbSelect('tbGrade', 'Grade', me.grade, grades)
      + tbSelect('tbLevel', 'Level', me.level,
                 [['','Standard'],['Honors','Honors'],['AP','AP']])
      + '<div class="tbfield"><label for="tbCourse">Course name</label>'
      + '<input id="tbCourse" type="text" value="' + esc(me.course)
      + '" placeholder="e.g. English III" /></div>'
      + tbSelect('tbDelivery', 'Delivery', me.delivery,
                 [['Live','Live class'],['On-Demand','On-Demand']])
      + '<div class="tbfield' + (me.delivery === 'Live' ? '' : ' off') + '" id="tbPeriodWrap">'
      + '<label for="tbPeriod">Class period</label>'
      + '<input id="tbPeriod" type="text" value="' + esc(me.period)
      + '" placeholder="e.g. 2" />'
      + '<span class="tbhint">Leave blank if it does not apply.</span></div>'
      + '</div></div></div>';

    var picker = '<div class="tbcard"><div class="tbhead"><span class="tbnum">2</span>'
      + '<span class="tbname">Choose your titles</span>'
      + '<span class="tbnote" id="tbScopeNote"></span></div>'
      + '<div class="tbpick">'
      + '<input id="tbSearch" type="search" placeholder="Search title or author&hellip;" '
      + 'aria-label="Search the catalogue" />'
      + '<button class="tick" id="tbScope" aria-pressed="' + (tbScope ? 'true' : 'false')
      + '">' + (tbScope ? 'Titles for my grade' : 'All ' + DATA.length + ' titles')
      + '</button>'
      + '<button class="tick" id="tbClear">Clear selection</button></div>'
      + '<div class="tblist" id="tbList"></div>'
      + '<div class="tbrun"><span class="tbrunN" id="tbN">0</span>'
      + '<span class="tbrunL">titles selected<br />for this course</span>'
      + '<span class="tbright">'
      + '<button class="tbbtn gh tbhide" id="tbCancel">Cancel edit</button>'
      + '<button class="tbbtn pri" id="tbSave" disabled>Save this course</button>'
      + '</span></div></div>';

    var mineCard = '<div class="tbcard tbhide" id="tbMineCard">'
      + '<div class="tbhead"><span class="tbnum">3</span>'
      + '<span class="tbname">My courses</span>'
      + '<span class="tbnote" id="tbMineNote"></span></div>'
      + '<div id="tbMineList"></div>'
      + '<div class="tbrun"><button class="tbbtn gh" id="tbAnother">Add another course</button>'
      + '</div></div>';

    var outCard = '<div class="tbcard tbhide" id="tbOutCard">'
      + '<div class="tbhead"><span class="tbnum">4</span>'
      + '<span class="tbname">Send this to your team</span>'
      + '<span class="tbnote"><button class="tick" id="tbCopyJson">Copy this block'
      + '</button></span></div>'
      + '<div class="tbbody"><div class="tbfile"><pre id="tbJson"></pre></div>'
      + '<div class="tbsay"><b>How this reaches the library.</b> Copy the block above '
      + 'and send it to whoever maintains the book lists. One record per course, in a '
      + 'file your team owns; a teacher with three courses is three records under the '
      + 'same name. Your shelf appears under Teacher Bookshelves once that file is '
      + 'published. Nothing you type here is sent anywhere on its own.</div>'
      + '</div></div>';

    return shell('My Classroom',
      'Tell us who you are and which titles you are teaching. You are choosing from the '
      + 'approved catalogue, so every title arrives already cleared for rights and edition '
      + 'and carries its purchase and free-text links with it. Teach more than one course? '
      + 'Save one, then add another &mdash; your name carries over.',
      form + picker + mineCard + outCard);
  }

  function tbDrawList(){
    var rows = tbCatalogue();
    var list = document.getElementById('tbList');
    if (!list) return;
    var h = '';
    for (var i=0;i<rows.length;i++){
      var r = rows[i];
      h += '<label class="tbtrow"><input type="checkbox" data-tbid="' + esc(r.id) + '"'
        + (tbPick[r.id] ? ' checked' : '') + ' />' + statePill(r.state)
        + '<span class="tbtmid"><span class="tbtt">' + esc(r.title) + '</span> '
        + '<span class="tbta">' + esc(r.authorDisplay || '') + '</span></span>'
        + '<span class="tbtg">Grade ' + esc(r.grade) + '</span></label>';
    }
    if (!rows.length) h = '<div class="tbblank">No titles match that search.</div>';
    list.innerHTML = h;
    var note = document.getElementById('tbScopeNote');
    if (note){
      note.textContent = tbScope
        ? rows.length + ' titles listed for Grade ' + me.grade
        : rows.length + ' of ' + DATA.length + ' titles';
    }
    var boxes = list.querySelectorAll('input[data-tbid]');
    for (var b=0;b<boxes.length;b++){
      boxes[b].addEventListener('change', (function(box){
        return function(){
          var id = box.getAttribute('data-tbid');
          if (box.checked) tbPick[id] = true; else delete tbPick[id];
          tbSync();
        };
      })(boxes[b]));
    }
    tbSync();
  }

  function tbSync(){
    var n = tbNPick();
    var nEl = document.getElementById('tbN');
    if (nEl) nEl.textContent = n;
    var save = document.getElementById('tbSave');
    if (save){
      save.disabled = !(n > 0 && me.teacher && me.course);
      save.textContent = (tbEdit >= 0) ? 'Update this course' : 'Save this course';
    }
    var cancel = document.getElementById('tbCancel');
    if (cancel) cancel.className = (tbEdit >= 0) ? 'tbbtn gh' : 'tbbtn gh tbhide';
    tbCount(n, 'title');
  }

  function tbClearCourse(){
    tbPick = {}; tbEdit = -1;
    me.course = ''; me.period = ''; me.level = ''; me.delivery = 'Live';
    saveMe();
    var c = document.getElementById('tbCourse'); if (c) c.value = '';
    var p = document.getElementById('tbPeriod'); if (p) p.value = '';
    var l = document.getElementById('tbLevel'); if (l) l.value = '';
    var d = document.getElementById('tbDelivery'); if (d) d.value = 'Live';
    tbSyncDelivery(); tbDrawList(); tbDrawMine();
  }

  function tbSyncDelivery(){
    var w = document.getElementById('tbPeriodWrap');
    if (w) w.className = (me.delivery === 'Live') ? 'tbfield' : 'tbfield off';
  }

  function tbDrawMine(){
    var card = document.getElementById('tbMineCard');
    var list = document.getElementById('tbMineList');
    if (!card || !list) return;
    if (!me.courses.length){ card.className = 'tbcard tbhide'; tbDrawJson(); return; }
    card.className = 'tbcard';
    var h = '';
    for (var i=0;i<me.courses.length;i++){
      var s = me.courses[i];
      h += '<div class="tbmrow' + (tbEdit === i ? ' on' : '') + '">'
        + '<span class="tbmc">' + esc(s.course) + '</span>'
        + '<span class="tbmm">' + tbBadges(s) + '</span>'
        + '<span class="tbmn">' + (s.titles || []).length + ' titles</span>'
        + '<span class="tbma">'
        + '<button class="tick" data-tbedit="' + i + '">Edit</button>'
        + '<button class="tick" data-tbdel="' + i + '">Remove</button>'
        + '</span></div>';
    }
    list.innerHTML = h;
    var note = document.getElementById('tbMineNote');
    if (note){
      note.textContent = me.courses.length
        + (me.courses.length === 1 ? ' course' : ' courses') + ' for ' + me.teacher;
    }
    var eb = list.querySelectorAll('[data-tbedit]');
    for (var e=0;e<eb.length;e++){
      eb[e].addEventListener('click', (function(btn){
        return function(){
          var n = parseInt(btn.getAttribute('data-tbedit'), 10);
          var s = me.courses[n];
          tbEdit = n;
          me.course = s.course; me.grade = s.grade; me.level = s.level;
          me.subject = s.subject; me.delivery = s.delivery; me.period = s.period || '';
          saveMe();
          var f = {tbCourse:me.course, tbGrade:me.grade, tbLevel:me.level,
                   tbSubject:me.subject, tbDelivery:me.delivery, tbPeriod:me.period};
          for (var k in f){
            var el = document.getElementById(k);
            if (el) el.value = f[k];
          }
          tbSyncDelivery();
          tbPick = {};
          for (var q=0;q<s.titles.length;q++) tbPick[s.titles[q]] = true;
          tbDrawList(); tbDrawMine();
          window.scrollTo({top: 0, behavior: 'smooth'});
        };
      })(eb[e]));
    }
    var db = list.querySelectorAll('[data-tbdel]');
    for (var d=0;d<db.length;d++){
      db[d].addEventListener('click', (function(btn){
        return function(){
          var n = parseInt(btn.getAttribute('data-tbdel'), 10);
          me.courses.splice(n, 1);
          if (tbEdit === n) tbEdit = -1;
          saveMe(); tbDrawMine(); tbSync();
        };
      })(db[d]));
    }
    tbDrawJson();
  }

  function tbRecords(){
    var recs = [];
    for (var i=0;i<me.courses.length;i++){
      var s = me.courses[i];
      recs.push({school_year: YEAR, teacher: s.teacher, course: s.course,
                 subject: s.subject, grade: s.grade, level: s.level || null,
                 delivery: s.delivery, period: s.period || null, titles: s.titles});
    }
    return {school_year: YEAR, classrooms: recs};
  }

  function tbJsonText(){ return JSON.stringify(tbRecords(), null, 2); }

  function tbDrawJson(){
    var card = document.getElementById('tbOutCard');
    var pre = document.getElementById('tbJson');
    if (!card || !pre) return;
    if (!me.courses.length){ card.className = 'tbcard tbhide'; return; }
    var txt = esc(tbJsonText())
      .replace(/&quot;([a-z_]+)&quot;:/g, '<span class="k">&quot;$1&quot;</span>:')
      .replace(/: &quot;([^&]*)&quot;/g, ': <span class="s">&quot;$1&quot;</span>')
      .replace(/^( +)&quot;([^&]+)&quot;(,?)$/gm, '$1<span class="s">&quot;$2&quot;</span>$3')
      .replace(/: null/g, ': <span class="n">null</span>');
    pre.innerHTML = txt;
    card.className = 'tbcard';
    var cj = document.getElementById('tbCopyJson');
    if (cj && !cj.getAttribute('data-wired')){
      cj.setAttribute('data-wired', '1');
      // Rebuilt at click time: this handler is bound once, so closing over a
      // render-time array would copy stale data after the next save.
      cj.addEventListener('click', function(){ tbToClipboard(tbJsonText(), cj); });
    }
  }

  function wireMine(){
    tbSyncDelivery();
    tbDrawList();
    tbDrawMine();

    var fields = [['tbTeacher','teacher'], ['tbCourse','course'], ['tbPeriod','period']];
    for (var i=0;i<fields.length;i++){
      (function(id, key){
        var el = document.getElementById(id);
        if (!el) return;
        el.addEventListener('input', function(){
          me[key] = el.value.trim();
          saveMe(); tbSync();
          if (key === 'teacher') tbDrawMine();
        });
      })(fields[i][0], fields[i][1]);
    }

    var selects = [['tbSubject','subject'], ['tbGrade','grade'],
                   ['tbLevel','level'], ['tbDelivery','delivery']];
    for (var s=0;s<selects.length;s++){
      (function(id, key){
        var el = document.getElementById(id);
        if (!el) return;
        el.addEventListener('change', function(){
          me[key] = el.value;
          saveMe();
          if (key === 'delivery') tbSyncDelivery();
          if (key === 'grade') tbDrawList();
          tbSync();
        });
      })(selects[s][0], selects[s][1]);
    }

    var scope = document.getElementById('tbScope');
    if (scope) scope.addEventListener('click', function(){
      tbScope = !tbScope;
      scope.setAttribute('aria-pressed', tbScope ? 'true' : 'false');
      scope.textContent = tbScope ? 'Titles for my grade' : 'All ' + DATA.length + ' titles';
      tbDrawList();
    });
    var search = document.getElementById('tbSearch');
    if (search) search.addEventListener('input', tbDrawList);
    var clr = document.getElementById('tbClear');
    if (clr) clr.addEventListener('click', function(){ tbPick = {}; tbDrawList(); });
    var another = document.getElementById('tbAnother');
    if (another) another.addEventListener('click', function(){
      tbClearCourse();
      var c = document.getElementById('tbCourse');
      if (c) c.focus();
      window.scrollTo({top: 0, behavior: 'smooth'});
    });
    var cancel = document.getElementById('tbCancel');
    if (cancel) cancel.addEventListener('click', tbClearCourse);

    var save = document.getElementById('tbSave');
    if (save) save.addEventListener('click', function(){
      var ids = [];
      for (var k in tbPick){ if (tbPick[k]) ids.push(k); }
      ids.sort();
      var rec = {teacher: me.teacher, course: me.course, subject: me.subject,
                 grade: me.grade, level: me.level,
                 delivery: me.delivery,
                 period: (me.delivery === 'Live' ? (me.period || null) : null),
                 titles: ids};
      if (tbEdit >= 0){ me.courses[tbEdit] = rec; }
      else {
        var hit = -1;
        for (var i=0;i<me.courses.length;i++){
          var c = me.courses[i];
          if (c.course.toLowerCase() === rec.course.toLowerCase()
           && c.delivery === rec.delivery
           && (c.period || '') === (rec.period || '')) hit = i;
        }
        if (hit >= 0) me.courses[hit] = rec; else me.courses.push(rec);
      }
      tbEdit = -1;
      saveMe(); tbDrawMine(); tbSync();
    });
  }

  /* ---- view: Teacher Bookshelves ---- */

  function tbAllShelves(){
    var out = [];
    for (var i=0;i<SHELVES.length;i++) out.push({s: SHELVES[i], draft: false});
    for (var j=0;j<me.courses.length;j++){
      var c = me.courses[j];
      if (c.teacher) out.push({s: c, draft: true});
    }
    return out;
  }

  function tbShelfHit(s){
    var q = (document.getElementById('tbFind') || {}).value || '';
    q = q.trim().toLowerCase();
    if (q){
      var hay = (s.teacher + ' ' + s.course + ' ' + (s.period || '') + ' '
                 + s.delivery).toLowerCase();
      if (hay.indexOf(q) === -1) return false;
    }
    var g = (document.getElementById('tbFindGrade') || {}).value || '';
    if (g && s.grade !== g) return false;
    var lv = (document.getElementById('tbFindLevel') || {}).value || '';
    if (lv === 'Standard' && s.level) return false;
    if (lv && lv !== 'Standard' && s.level !== lv) return false;
    var d = (document.getElementById('tbFindDelivery') || {}).value || '';
    if (d && s.delivery !== d) return false;
    return true;
  }

  function tbDrawShelves(){
    var box = document.getElementById('tbShelfGrid');
    if (!box) return;
    var all = tbAllShelves();
    var rows = [];
    for (var i=0;i<all.length;i++){ if (tbShelfHit(all[i].s)) rows.push(all[i]); }
    rows.sort(function(a, b){
      if (a.draft !== b.draft) return a.draft ? 1 : -1;
      if (a.s.teacher !== b.s.teacher) return a.s.teacher < b.s.teacher ? -1 : 1;
      return a.s.course < b.s.course ? -1 : 1;
    });
    tbRendered = rows;
    var h = '';
    for (var r=0;r<rows.length;r++) h += tbShelfCard(rows[r].s, rows[r].draft, r);
    if (!rows.length){
      h = '<div class="tbblank">' + (all.length
        ? 'No bookshelf matches that search.'
        : 'No bookshelves published yet. Teachers build one under <b>My Classroom</b>; '
          + 'they appear here once the team publishes <b>classrooms.json</b>.') + '</div>';
    }
    box.innerHTML = h;
    var hits = document.getElementById('tbHits');
    if (hits) hits.textContent = rows.length + (rows.length === 1 ? ' course' : ' courses');
    tbCount(rows.length, 'course');

    var pb = box.querySelectorAll('[data-tbprint]');
    for (var p=0;p<pb.length;p++){
      pb[p].addEventListener('click', (function(btn){
        return function(){ tbPrintShelf(parseInt(btn.getAttribute('data-tbprint'), 10)); };
      })(pb[p]));
    }
    var cb = box.querySelectorAll('[data-tbcopy]');
    for (var c=0;c<cb.length;c++){
      cb[c].addEventListener('click', (function(btn){
        return function(){
          var row = tbRendered[parseInt(btn.getAttribute('data-tbcopy'), 10)];
          if (row) tbToClipboard(tbShelfText(row.s), btn);
        };
      })(cb[c]));
    }
  }

  function viewShelves(){
    var total = SHELVES.length;
    var teachers = {};
    for (var i=0;i<SHELVES.length;i++) teachers[SHELVES[i].teacher] = true;
    var nT = 0; for (var t in teachers) nT++;

    var grades = '<option value="">All grades</option>';
    for (var g=0;g<GRADE_LIST.length;g++){
      grades += '<option value="' + GRADE_LIST[g] + '">Grade ' + GRADE_LIST[g] + '</option>';
    }

    var strip = '<div class="tbstrip"><div class="tbstripItem">'
      + '<span class="tbstripN">' + total + '</span>'
      + '<span class="tbstripL">' + (total === 1 ? 'course' : 'courses')
      + ' published<br />' + (YEAR ? 'for ' + esc(YEAR) : '&nbsp;') + '</span></div>'
      + '<div class="tbstripItem"><span class="tbstripN">' + nT + '</span>'
      + '<span class="tbstripL">' + (nT === 1 ? 'teacher' : 'teachers')
      + '<br />with a shelf</span></div></div>';

    var find = '<div class="tbfind">'
      + '<input id="tbFind" type="search" placeholder="Search by teacher or course&hellip;" '
      + 'aria-label="Search bookshelves" />'
      + '<select id="tbFindGrade">' + grades + '</select>'
      + '<select id="tbFindLevel"><option value="">All levels</option>'
      + '<option value="Standard">Standard</option>'
      + '<option value="Honors">Honors</option><option value="AP">AP</option></select>'
      + '<select id="tbFindDelivery"><option value="">Live and On-Demand</option>'
      + '<option value="Live">Live only</option>'
      + '<option value="On-Demand">On-Demand only</option></select>'
      + '<span class="tbhits" id="tbHits"></span></div>';

    return shell('Teacher Bookshelves',
      'What each teacher has selected from the approved catalogue, with the purchase and '
      + 'free-text links carried over from the Reference Library entry. Search by teacher '
      + 'or by course &mdash; both find the same shelf.',
      strip + find + '<div class="tbshelves" id="tbShelfGrid"></div>');
  }

  function wireShelves(){
    tbDrawShelves();
    var ids = ['tbFind', 'tbFindGrade', 'tbFindLevel', 'tbFindDelivery'];
    for (var i=0;i<ids.length;i++){
      var el = document.getElementById(ids[i]);
      if (!el) continue;
      el.addEventListener(ids[i] === 'tbFind' ? 'input' : 'change', tbDrawShelves);
    }
  }

  var VIEWS = {compare:viewCompare, grades:viewGrades, sources:viewSources,
               attention:viewAttention, mine:viewMine, shelves:viewShelves};

  // Views that render their own interactive body and set their own count.
  var VIEW_WIRE = {mine:wireMine, shelves:wireShelves};

  function drawView(){
    grid.style.display = 'none';
    viewsEl.hidden = false;
    viewsEl.innerHTML = VIEWS[view]();
    if (!VIEW_WIRE[view]){
      var n = viewsEl.querySelectorAll('table.vt tbody tr').length;
      countEl.textContent = n + ' row' + (n===1?'':'s');
    }
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
    // The two teacher views build their own controls, so they bind after the
    // shared row wiring above rather than instead of it.
    if (VIEW_WIRE[view]) VIEW_WIRE[view]();
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
