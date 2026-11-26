/* Sites Preview site behaviour (feature library, site-v2 parity). Progressive enhancement: pages work without JS. Created by Rohan Kells. */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); }, $$ = function (s, r) { return [].slice.call((r || document).querySelectorAll(s)); };
  var store = { get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } }, set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} } };
  var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  /* theme toggle */
  $$('.theme-toggle').forEach(function (b) {
    var sync = function () { var dk = document.documentElement.getAttribute('data-scheme') === 'dark'; b.setAttribute('aria-pressed', String(dk)); b.setAttribute('aria-label', dk ? 'Switch to light mode' : 'Switch to dark mode'); };
    sync(); b.addEventListener('click', function () { var d = document.documentElement, n = d.getAttribute('data-scheme') === 'dark' ? 'light' : 'dark'; d.setAttribute('data-scheme', n); store.set('theme', n); sync(); });
  });
  /* menus: one open at a time, Escape closes, click outside closes */
  var drops = $$('header details');
  drops.forEach(function (d) {
    d.addEventListener('toggle', function () { if (d.open) drops.forEach(function (o) { if (o !== d) o.open = false; }); });
    d.addEventListener('keydown', function (e) { if (e.key === 'Escape' && d.open) { d.open = false; $('summary', d).focus(); } });
  });
  document.addEventListener('click', function (e) { drops.forEach(function (d) { if (d.open && !d.contains(e.target)) d.open = false; }); });
  /* cookie consent */
  var consent = $('#consent'), queue = [];
  window.SP = { loadOptional: function (fn) { if (store.get('consent') === 'accepted') fn(); else queue.push(fn); } };
  var show = function (on) { if (consent) { consent.hidden = !on; document.body.classList.toggle('has-consent', on); } };
  if (consent) {
    if (!store.get('consent')) show(true);
    $$('[data-consent]', consent).forEach(function (b) { b.addEventListener('click', function () { store.set('consent', b.dataset.consent); show(false); if (b.dataset.consent === 'accepted') queue.splice(0).forEach(function (f) { f(); }); }); });
    $$('[data-cookie-settings]').forEach(function (b) { b.addEventListener('click', function () { show(true); $('button', consent).focus(); }); });
  }
  /* chat panel */
  var cb = $('#chat-toggle'), cp = $('#chat-panel');
  if (cb && cp) {
    cb.setAttribute('role', 'button');
    var open = function (on) { cp.hidden = !on; cb.setAttribute('aria-expanded', String(on)); document.body.classList.toggle('chat-open', on); if (on) { var f = $('input,textarea', cp); if (f) f.focus(); } else cb.focus(); };
    cb.addEventListener('click', function (e) { e.preventDefault(); open(cp.hidden); });
    $$('[data-chat-close]', cp).forEach(function (b) { b.addEventListener('click', function () { open(false); }); });
    cp.addEventListener('keydown', function (e) { if (e.key === 'Escape') open(false); });
    var foot = $('footer.site');
    var lift = function () { var over = innerHeight - foot.getBoundingClientRect().top; cb.style.transform = over > 0 ? 'translateY(' + (-over) + 'px)' : ''; };
    if (foot) { addEventListener('scroll', lift, { passive: true }); addEventListener('resize', lift); lift(); }
  }
  /* forms */
  var tomorrow = function () { var d = new Date(); d.setDate(d.getDate() + 1); return d.toISOString().slice(0, 10); };
  $$('input[type=date][data-weekday]').forEach(function (i) { i.min = tomorrow(); });
  var setErr = function (el, msg) {
    if (!el.id) return; var id = el.id + '-err', e = document.getElementById(id);
    if (!e) { e = document.createElement('p'); e.id = id; e.className = 'field-error'; (el.closest('label') || el).insertAdjacentElement('afterend', e); }
    e.textContent = msg || ''; e.hidden = !msg;
    if (msg) { el.setAttribute('aria-invalid', 'true'); el.setAttribute('aria-describedby', id); } else { el.removeAttribute('aria-invalid'); el.removeAttribute('aria-describedby'); }
  };
  var check = function (f) {
    var first = null;
    [].forEach.call(f.elements, function (el) {
      if (!el.name || el.type === 'hidden' || el.closest('[hidden]')) return;
      var m = '';
      if (!el.checkValidity()) m = el.type === 'checkbox' ? 'Please tick this box to continue.' : el.type === 'email' ? 'Please enter a valid email address.' : el.type === 'url' ? 'Please enter a full link starting with https://' : 'Please complete this field.';
      if (!m && el.dataset.weekday !== undefined && el.value) { var d = new Date(el.value + 'T00:00:00'); if (el.value < tomorrow()) m = 'Please choose a date from tomorrow onwards.'; else if (d.getDay() === 0 || d.getDay() === 6) m = 'Please choose a weekday (Monday to Friday).'; }
      setErr(el, m); if (m && !first) first = el;
    });
    if (first) first.focus(); return !first;
  };
  $$('form.cf').forEach(function (f) {
    f.noValidate = true; var msg = $('.form-msg', f);
    f.addEventListener('submit', function (e) {
      e.preventDefault(); msg.className = 'form-msg'; msg.textContent = '';
      if (!check(f)) { msg.className = 'form-msg err'; msg.textContent = 'Please check the highlighted fields.'; return; }
      var btn = $('[type=submit]', f), lab = btn.innerHTML; btn.disabled = true; btn.setAttribute('aria-busy', 'true'); btn.textContent = 'Sending…';
      var data = new URLSearchParams(new FormData(f)); data.set('page', location.pathname);
      fetch(f.getAttribute('action'), { method: 'POST', headers: { Accept: 'application/json' }, body: data })
        .then(function (r) { return r.json().catch(function () { return { ok: r.ok }; }).then(function (j) { if (!r.ok || j.ok === false) throw j; return j; }); })
        .then(function (j) {
          var box = document.createElement('div'); box.className = 'form-success'; box.setAttribute('role', 'status'); box.tabIndex = -1;
          var h = document.createElement('h3'); h.textContent = 'Thank you'; var p = document.createElement('p');
          p.textContent = (f.dataset.success || 'Your message was received. We will reply by email.') + (j.id ? ' Reference: ' + j.id + '.' : ''); box.appendChild(h); box.appendChild(p);
          f.replaceWith(box); box.focus();
        })
        .catch(function (j) { msg.className = 'form-msg err'; msg.textContent = (j && j.error) || 'Sorry, the message could not be sent. Please email us instead.'; })
        .then(function () { if (btn.isConnected) { btn.disabled = false; btn.removeAttribute('aria-busy'); btn.innerHTML = lab; } });
    });
  });
  /* help centre search + filter */
  var hl = $('#help-list'), ht = $('[data-help]');
  if (hl && ht) {
    ht.hidden = false; var q = $('#help-q'), chips = $$('.chip', ht), none = $('.filter-none'), cnt = $('#help-count'), grp = 'all';
    var run = function () { var s = q.value.trim().toLowerCase(), n = 0;
      $$('li', hl).forEach(function (li) { var on = (grp === 'all' || li.dataset.group === grp) && (!s || li.textContent.toLowerCase().indexOf(s) > -1); li.hidden = !on; if (on) n++; });
      none.hidden = n > 0; cnt.textContent = n + (n === 1 ? ' article' : ' articles'); };
    q.addEventListener('input', run);
    chips.forEach(function (c) { c.addEventListener('click', function () { grp = c.dataset.group; chips.forEach(function (o) { o.setAttribute('aria-pressed', String(o === c)); }); run(); }); });
    run();
  }
  /* status page: real checks only */
  var st = $('[data-status-page]');
  if (st) {
    var set = function (k, t, ok) { var c = $('[data-status=' + k + ']'); if (c) { c.textContent = t; c.className = 'pill' + (ok === undefined ? '' : ok ? ' ok' : ' bad'); } };
    var run2 = function () { var t0 = performance.now();
      fetch('/api/health', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (j) { set('website', 'Operational', true); set('forms', j.forms === 'operational' ? 'Operational' : 'Unavailable', j.forms === 'operational'); set('ms', Math.round(performance.now() - t0) + ' ms'); })
        .catch(function () { set('website', 'Operational', true); set('forms', 'Unavailable', false); set('ms', 'no response'); })
        .then(function () { set('time', new Date().toLocaleString('en-AU', { dateStyle: 'medium', timeStyle: 'short' })); }); };
    run2(); var rb = $('[data-status-recheck]'); if (rb) rb.addEventListener('click', run2);
  }
  /* age gate */
  var ag = $('#age-gate');
  if (ag && document.documentElement.classList.contains('age-pending')) {
    var yes = $('[data-age=yes]', ag); setTimeout(function () { yes.focus(); }, 0);
    ag.addEventListener('keydown', function (e) { if (e.key !== 'Tab') return; var f = $$('button,a', ag), i = f.indexOf(document.activeElement);
      if (e.shiftKey && i <= 0) { e.preventDefault(); f[f.length - 1].focus(); } else if (!e.shiftKey && i === f.length - 1) { e.preventDefault(); f[0].focus(); } });
    yes.addEventListener('click', function () { store.set('age_ok', String(Date.now())); document.documentElement.classList.remove('age-pending'); var m = $('#main'); if (m) m.focus(); });
  }
  /* mobile CTA bar hides while a form field has focus */
  document.addEventListener('focusin', function (e) { if (e.target.matches('input,textarea,select')) document.body.classList.add('form-focus'); });
  document.addEventListener('focusout', function (e) { if (e.target.matches('input,textarea,select')) document.body.classList.remove('form-focus'); });
  /* print: open details */
  addEventListener('beforeprint', function () { $$('details').forEach(function (d) { if (!d.open) { d.dataset.wasClosed = '1'; d.open = true; } }); });
  addEventListener('afterprint', function () { $$('details[data-was-closed]').forEach(function (d) { d.open = false; delete d.dataset.wasClosed; }); });
  /* print */
  $$('[data-print]').forEach(function (b) { b.hidden = false; b.addEventListener('click', function () { print(); }); });
  /* scroll reveal */
  if (!reduced && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } }); }, { rootMargin: '0px 0px -40px 0px' });
    $$('main .blk, main .card, main .band').forEach(function (el) { if (el.getBoundingClientRect().top > innerHeight) { el.classList.add('reveal'); io.observe(el); } });
  }
  /* promos: date-swapped (urgent bar wins: promos are not rendered when it is active) */
  var today = new Date().toISOString().slice(0, 10);
  $$('.promo[data-start]').forEach(function (p) { p.hidden = !(today >= p.dataset.start && today <= p.dataset.end); });
  /* careers: expired roles hide */
  $$('.job[data-valid-through]').forEach(function (j) { if (j.dataset.validThrough < today) j.hidden = true; });
  var jg = $('.job') && $('.job').parentElement; if (jg && !$$('.job', jg).some(function (j) { return !j.hidden; })) { var nn = $('.filter-none', jg.parentElement); if (nn) nn.hidden = false; }
  /* portfolio filter */
  var pf = $('[data-pf]');
  if (pf) { pf.hidden = false; $$('.chip', pf).forEach(function (c) { c.addEventListener('click', function () { var t = c.dataset.tag;
    $$('.chip', pf).forEach(function (o) { o.setAttribute('aria-pressed', String(o === c)); });
    $$('.pf').forEach(function (x) { x.hidden = !(t === 'all' || x.dataset.tags.split('|').indexOf(t) > -1); }); }); }); }
  /* referral code: /r/<code> stores it (first-party cookie, 30 days) and every form sends it in a hidden field */
  var rc = $('[data-ref-code]');
  if (rc) document.cookie = 'ref=' + encodeURIComponent(rc.dataset.refCode) + ';max-age=2592000;path=/;SameSite=Lax';
  var refm = /(?:^|; )ref=([^;]+)/.exec(document.cookie);
  if (refm) $$('input[name=ref]').forEach(function (i) { i.value = decodeURIComponent(refm[1]); });
  /* multi-step lead form with 30-day autosave (no JS: one long form) */
  $$('form.ms').forEach(function (f) {
    var steps = $$('.step', f), i = 0, key = 'autosave:' + location.pathname, prev = $('[data-ms-prev]', f), next = $('[data-ms-next]', f), sub = $('[type=submit]', f), clr = $('[data-autosave-clear]');
    var show = function () { steps.forEach(function (s, n) { s.hidden = n !== i; }); prev.hidden = i === 0; next.hidden = i === steps.length - 1; sub.hidden = i !== steps.length - 1;
      var c = $('.consent', f); if (c) c.hidden = i !== steps.length - 1; };
    var valid = function () { var ok = true; $$('input,select,textarea', steps[i]).forEach(function (el) { if (!el.checkValidity()) { ok = false; setErr(el, el.type === 'email' ? 'Please enter a valid email address.' : 'Please complete this field.'); } else setErr(el, ''); }); return ok; };
    next.addEventListener('click', function () { if (valid()) { i++; show(); var fe = $('input,select,textarea', steps[i]); if (fe) fe.focus(); } });
    prev.addEventListener('click', function () { i--; show(); });
    try { var s = JSON.parse(store.get(key) || 'null'); if (s && Date.now() - s.t < 2592e6) { Object.keys(s.v).forEach(function (k) { var el = f.elements[k]; if (el && el.type !== 'hidden' && el.type !== 'checkbox') el.value = s.v[k]; }); if (clr) clr.hidden = false; } else if (s) localStorage.removeItem(key); } catch (e) {}
    f.addEventListener('input', function () { var v = {}; [].forEach.call(f.elements, function (el) { if (el.name && el.type !== 'hidden' && el.type !== 'checkbox' && el.name !== 'website_hp') v[el.name] = el.value; }); store.set(key, JSON.stringify({ t: Date.now(), v: v })); if (clr) clr.hidden = false; });
    f.addEventListener('submit', function () { setTimeout(function () { if (!f.isConnected) { try { localStorage.removeItem(key); } catch (e) {} } }, 1500); });
    if (clr) clr.addEventListener('click', function () { try { localStorage.removeItem(key); } catch (e) {} f.reset(); i = 0; show(); clr.hidden = true; });
    show();
  });
  /* cookie-free heat map: only when switched on for this site; no cookies, IDs or IP storage; honours DNT and GPC */
  if (document.documentElement.hasAttribute('data-heatmap') && navigator.doNotTrack !== '1' && !navigator.globalPrivacyControl && navigator.sendBeacon) {
    var buf = [];
    document.addEventListener('click', function (e) { var de = document.documentElement; buf.push({ p: location.pathname, x: Math.round(e.pageX / de.clientWidth * 1000) / 10, y: Math.round(e.pageY), w: de.clientWidth < 769 ? 'm' : 'd' }); if (buf.length >= 20) flush(); }, { passive: true });
    var flush = function () { if (buf.length) { navigator.sendBeacon('/api/heatmap', JSON.stringify(buf.splice(0))); } };
    addEventListener('pagehide', flush);
  }
  /* site-content answer engine: offline BM25 over /assets/search-index.json; hook for a Worker later via data-chat-api */
  var askF = $('[data-ask]');
  if (askF) {
    var out = $('.ask-out'), IDX = null, api = document.documentElement.getAttribute('data-chat-api');
    var STOP = 'a an and are as at be by can do does for from has have how i if in is it of on or our that the this to was we what when where which who why will with you your'.split(' ');
    var tok = function (s) { return (s.toLowerCase().match(/[a-z0-9]+/g) || []).filter(function (w) { return w.length > 1 && STOP.indexOf(w) < 0; }).map(function (w) { return w.replace(/(ing|ies|es|s)$/, ''); }); };
    var load = function () { return IDX ? Promise.resolve(IDX) : fetch('/assets/search-index.json').then(function (r) { return r.json(); }).then(function (j) {
      var N = j.docs.length, df = {}, tot = 0; j.docs.forEach(function (d) { d.tk = tok(d.t + ' ' + d.h + ' ' + d.x); tot += d.tk.length; var seen = {}; d.tk.forEach(function (w) { if (!seen[w]) { seen[w] = 1; df[w] = (df[w] || 0) + 1; } }); });
      IDX = { docs: j.docs, df: df, N: N, avg: tot / Math.max(N, 1) }; return IDX; }); };
    var bm25 = function (q) { var k1 = 1.2, b = 0.75, qt = tok(q);
      return IDX.docs.map(function (d) { var tf = {}, s = 0; d.tk.forEach(function (w) { tf[w] = (tf[w] || 0) + 1; });
        qt.forEach(function (w) { if (!tf[w]) return; var idf = Math.log(1 + (IDX.N - IDX.df[w] + 0.5) / (IDX.df[w] + 0.5)); s += idf * tf[w] * (k1 + 1) / (tf[w] + k1 * (1 - b + b * d.tk.length / IDX.avg)); });
        return { d: d, s: s }; }).filter(function (r) { return r.s > 0; }).sort(function (a, c) { return c.s - a.s; }); };
    var render = function (q, res) { out.innerHTML = ''; var seenU = {}, n = 0;
      res.forEach(function (r) { if (n >= 3 || seenU[r.d.u + r.d.h]) return; seenU[r.d.u + r.d.h] = 1; n++;
        var a = document.createElement('div'); a.className = 'ans'; var l = document.createElement('a'); l.href = r.d.u; l.textContent = r.d.t + (r.d.h ? ' — ' + r.d.h : '');
        var p = document.createElement('p'); p.textContent = r.d.x.length > 220 ? r.d.x.slice(0, 217) + '…' : r.d.x; a.appendChild(l); a.appendChild(p); out.appendChild(a); });
      var h = document.createElement('p'); h.className = 'sub'; h.textContent = n ? 'Not what you needed? Ask us below and we will reply by email.' : 'No answer found on this site. Ask us below and we will reply by email.'; out.appendChild(h);
      var m = $('#chat-msg'); if (m && !m.value) m.value = q; };
    window.SP.answer = function (q) { return api ? fetch(api, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ q: q }) }).then(function (r) { return r.json(); }) : load().then(function () { return bm25(q); }); };
    askF.addEventListener('submit', function (e) { e.preventDefault(); var q = $('#ask-q').value.trim(); if (!q) return; out.textContent = 'Searching this site…';
      load().then(function () { render(q, bm25(q)); }).catch(function () { out.textContent = 'Search is unavailable right now. Please ask us below.'; }); });
  }
  /* spam protection: fill-time stamp on every form; Turnstile widget only when this site has a key (live on Cloudflare) */
  var t0 = String(Date.now()), tsk = document.documentElement.getAttribute('data-turnstile');
  $$('form.cf').forEach(function (f) { var i = document.createElement('input'); i.type = 'hidden'; i.name = 'ts'; i.value = t0; f.appendChild(i);
    if (tsk) { var w = document.createElement('div'); w.className = 'cf-turnstile full'; w.setAttribute('data-sitekey', tsk); var sb = f.querySelector('[type=submit]'); (sb ? sb.closest('div') : f).insertAdjacentElement('beforebegin', w); } });
  if (tsk) { var tsc = document.createElement('script'); tsc.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js'; tsc.async = true; tsc.defer = true; document.head.appendChild(tsc); }
  /* newsletter double opt-in confirmation */
  var nl = $('[data-nl-confirm]');
  if (nl) { var tk = new URLSearchParams(location.search).get('token'), ns = $('.nl-status', nl);
    if (tk) fetch('/api/newsletter/confirm?token=' + encodeURIComponent(tk)).then(function (r) { return r.json(); }).then(function (j) { ns.textContent = j.ok ? 'Thanks — your subscription is confirmed.' : j.error; }).catch(function () { ns.textContent = 'We could not confirm right now. Please try the link again later.'; }); }
  /* site search (page + header shortcut) using the same build-time index */
  var idxP = null, getIdx = function () { return idxP || (idxP = fetch('/assets/search-index.json').then(function (r) { return r.json(); })); };
  var so = $('#search-out'), sf = $('[data-site-search]');
  if (sf && so) {
    var runS = function (q) { q = q.trim().toLowerCase(); if (!q) { so.textContent = ''; return; } getIdx().then(function (j) { var ws = q.split(/\s+/), seen = {}, hits = j.docs.map(function (d) { var t = (d.t + ' ' + d.h + ' ' + d.x).toLowerCase(), s = 0; ws.forEach(function (w) { var i = t.indexOf(w); while (i > -1) { s++; i = t.indexOf(w, i + 1); } }); return { d: d, s: s }; }).filter(function (h) { return h.s > 0; }).sort(function (a, b) { return b.s - a.s; });
      so.innerHTML = ''; var n = 0; hits.forEach(function (h) { if (n >= 12 || seen[h.d.u + h.d.h]) return; seen[h.d.u + h.d.h] = 1; n++; var a = document.createElement('div'); a.className = 'ans'; var l = document.createElement('a'); l.href = h.d.u; l.textContent = h.d.t + (h.d.h ? ' — ' + h.d.h : ''); var p = document.createElement('p'); p.textContent = h.d.x.slice(0, 200) + (h.d.x.length > 200 ? '…' : ''); a.appendChild(l); a.appendChild(p); so.appendChild(a); });
      var c = document.createElement('p'); c.className = 'sub'; c.textContent = n ? n + ' result' + (n === 1 ? '' : 's') : 'No results. Try another word or ask us on the contact page.'; so.insertBefore(c, so.firstChild); }); };
    var q0 = new URLSearchParams(location.search).get('q'); if (q0) { $('#sq').value = q0; runS(q0); }
    sf.addEventListener('submit', function (e) { e.preventDefault(); var q = $('#sq').value; history.replaceState(null, '', '?q=' + encodeURIComponent(q)); runS(q); });
  }
  /* keyboard shortcuts */
  var kh = $('.kbd-help'), gPend = 0;
  var typing = function (e) { var t = e.target; return t.isContentEditable || /^(input|textarea|select)$/i.test(t.tagName); };
  document.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); if ($('#sq')) $('#sq').focus(); else location.href = '/search/'; return; }
    if (typing(e) || e.altKey || e.ctrlKey || e.metaKey) return;
    if (e.key === '/') { e.preventDefault(); if ($('#sq')) $('#sq').focus(); else location.href = '/search/'; }
    else if (e.key === '?') { kh.hidden = false; $('button', kh).focus(); }
    else if (e.key === 'Escape') { kh.hidden = true; var ep = $('.exit-prompt'); if (ep) ep.hidden = true; }
    else if (e.key === 't') { var tb = $('.theme-toggle'); if (tb) tb.click(); }
    else if (e.key === 'g') { gPend = Date.now(); }
    else if (e.key === 'h' && Date.now() - gPend < 1200) { location.href = '/'; }
  });
  if (kh) $('[data-kbd-close]', kh).addEventListener('click', function () { kh.hidden = true; });
  /* back to top + reading progress */
  var tt = $('.to-top'), pb = $('.progress span');
  var onScroll = function () { var de = document.documentElement, max = de.scrollHeight - innerHeight; if (pb) pb.style.transform = 'scaleX(' + (max > 0 ? Math.min(1, scrollY / max) : 0) + ')'; if (tt) tt.hidden = scrollY < 600; };
  addEventListener('scroll', onScroll, { passive: true }); onScroll();
  if (tt) tt.addEventListener('click', function () { scrollTo({ top: 0, behavior: reduced ? 'auto' : 'smooth' }); var m = $('#main'); if (m) m.focus({ preventScroll: true }); });
  /* counters (real counts from this site) */
  var cs = $$('[data-count]');
  if (cs.length && !reduced && 'IntersectionObserver' in window) { var co = new IntersectionObserver(function (es) { es.forEach(function (e) { if (!e.isIntersecting) return; co.unobserve(e.target); var el = e.target, n = +el.dataset.count, t0c = performance.now();
    var step = function (now) { var k = Math.min(1, (now - t0c) / 900); el.textContent = Math.round(n * (1 - Math.pow(1 - k, 3))); if (k < 1) requestAnimationFrame(step); }; requestAnimationFrame(step); }); }); cs.forEach(function (c) { co.observe(c); }); }
  /* map: loads OpenStreetMap only on request */
  $$('[data-map-load]').forEach(function (b) { b.addEventListener('click', function () { var f = document.createElement('iframe'); f.title = 'Map of Australia (OpenStreetMap)'; f.loading = 'lazy'; f.src = 'https://www.openstreetmap.org/export/embed.html?bbox=112.5%2C-44.5%2C154.5%2C-9.5&layer=mapnik'; f.width = '100%'; f.height = '360'; f.style.border = '0'; b.closest('[data-map]').replaceChildren(f); }); });
  /* resource filter */
  var rf = $('[data-rf]');
  if (rf) { rf.hidden = false; $$('.chip', rf).forEach(function (c) { c.addEventListener('click', function () { var t = c.dataset.rtag; $$('.chip', rf).forEach(function (o) { o.setAttribute('aria-pressed', String(o === c)); }); $$('.res').forEach(function (x) { x.hidden = !(t === 'all' || x.dataset.rtag === t); }); }); }); }
  /* exit-intent help prompt: desktop only, once per session, never on top of the age gate */
  var ex = $('.exit-prompt');
  if (ex && matchMedia('(pointer:fine) and (min-width: 900px)').matches) {
    document.addEventListener('mouseout', function (e) { if (e.relatedTarget || e.clientY > 10) return; try { if (sessionStorage.getItem('exit_shown')) return; sessionStorage.setItem('exit_shown', '1'); } catch (er) { return; }
      if (document.documentElement.classList.contains('age-pending')) return; ex.hidden = false; $('a', ex).focus(); });
    $('[data-exit-close]', ex).addEventListener('click', function () { ex.hidden = true; });
  }
  $$('[data-to-top]').forEach(function (b) { b.addEventListener('click', function () { scrollTo({ top: 0, behavior: reduced ? 'auto' : 'smooth' }); var m = $('#main'); if (m) m.focus({ preventScroll: true }); }); });
})();
  /* Shared social links. Loads /_core/social/client.js Empty or unchanged sites stay as they are. Created by Rohan Kells. */
  (function () {
    var s = document.createElement('script');
    s.src = '/_core/social/client.js';
    s.defer = true;
    s.onerror = function () {};
    document.head.appendChild(s);
  })();
/* ==== mobile-pass 1.0 (25 Nov 2026): footer accordion, mobile nav overlay, step icons, centred icon cards, Get a quote button, stepped form cards. Progressive enhancement: without JS pages work as before. Created by Rohan Kells. Icons: Lucide (ISC licence). ==== */
(function () {
  'use strict';
  if (window.__mpPass) return; window.__mpPass = 1;
  var D = document, H = D.documentElement, $$ = function (s, r) { return [].slice.call((r || D).querySelectorAll(s)); };
  H.classList.add('mp-js');
  var ICONS = {"badge-check":"<path d=\"M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76Z\"/><path d=\"m16 9-5.5 5.5L8 12\"/>","bell":"<path d=\"M10.268 21a2 2 0 0 0 3.464 0\"/><path d=\"M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326\"/>","book-open":"<path d=\"M12 5v16\"/><path d=\"M20.001 19A2 2 0 0022 17V5a2 2 0 00-1.999-2L16 3.002A5 5 0 0012 5a5 5 0 00-4-2H4a2 2 0 00-2 2v12a2 2 0 001.999 2H8a5 5 0 014 2 5 5 0 014-2z\"/>","calendar-check":"<path d=\"M8 2v3\"/><path d=\"M16 2v3\"/><rect x=\"3\" y=\"3\" width=\"18\" height=\"18\" rx=\"2\"/><path d=\"M3 9h18\"/><path d=\"m9 15 2 2 4-4\"/>","chart-no-axes-column":"<path d=\"M5 21v-6\"/><path d=\"M12 21V3\"/><path d=\"M19 21V9\"/>","circle-check-big":"<path d=\"M21.801 10A10 10 0 1 1 17 3.335\"/><path d=\"m9 11 3 3L22 4\"/>","clipboard-list":"<rect width=\"8\" height=\"4\" x=\"8\" y=\"2\" rx=\"1\" ry=\"1\"/><path d=\"M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2\"/><path d=\"M12 11h4\"/><path d=\"M12 16h4\"/><path d=\"M8 11h.01\"/><path d=\"M8 16h.01\"/>","download":"<path d=\"M12 15V3\"/><path d=\"M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4\"/><path d=\"m7 10 5 5 5-5\"/>","eye":"<path d=\"M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0\"/><circle cx=\"12\" cy=\"12\" r=\"3\"/>","file-text":"<path d=\"M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.704.706l3.588 3.588A2.4 2.4 0 0 1 20 8v12a2 2 0 0 1-2 2z\"/><path d=\"M14 2v5a1 1 0 0 0 1 1h5\"/><path d=\"M10 9H8\"/><path d=\"M16 13H8\"/><path d=\"M16 17H8\"/>","flag":"<path d=\"M4 22V4a1 1 0 0 1 .4-.8A6 6 0 0 1 8 2c3 0 5 2 7.333 2q2 0 3.067-.8A1 1 0 0 1 20 4v10a1 1 0 0 1-.4.8A6 6 0 0 1 16 16c-3 0-5-2-8-2a6 6 0 0 0-4 1.528\"/>","gauge":"<path d=\"m12 14 4-4\"/><path d=\"M3.34 19a10 10 0 1 1 17.32 0\"/>","graduation-cap":"<path d=\"M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z\"/><path d=\"M22 10v6\"/><path d=\"M6 12.5V16a6 3 0 0 0 12 0v-3.5\"/>","hammer":"<path d=\"m15 12-9.373 9.373a1 1 0 0 1-3.001-3L12 9\"/><path d=\"m18 15 4-4\"/><path d=\"m21.5 11.5-1.914-1.914A2 2 0 0 1 19 8.172v-.344a2 2 0 0 0-.586-1.414l-1.657-1.657A6 6 0 0 0 12.516 3H9l1.243 1.243A6 6 0 0 1 12 8.485V10l2 2h1.172a2 2 0 0 1 1.414.586L18.5 14.5\"/>","handshake":"<path d=\"m11 17 2 2a1 1 0 1 0 3-3\"/><path d=\"m14 14 2.5 2.5a1 1 0 1 0 3-3l-3.88-3.88a3 3 0 0 0-4.24 0l-.88.88a1 1 0 1 1-3-3l2.81-2.81a5.79 5.79 0 0 1 7.06-.87l.47.28a2 2 0 0 0 1.42.25L21 4\"/><path d=\"m21 3 1 11h-2\"/><path d=\"M3 3 2 14l6.5 6.5a1 1 0 1 0 3-3\"/><path d=\"M3 4h8\"/>","hard-drive":"<path d=\"M10 16h.01\"/><path d=\"M2.212 11.577a2 2 0 0 0-.212.896V18a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-5.527a2 2 0 0 0-.212-.896L18.55 5.11A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z\"/><path d=\"M21.946 12.013H2.054\"/><path d=\"M6 16h.01\"/>","heart":"<path d=\"M2 9.5a5.5 5.5 0 0 1 9.591-3.676.56.56 0 0 0 .818 0A5.49 5.49 0 0 1 22 9.5c0 2.29-1.5 4-3 5.5l-5.492 5.313a2 2 0 0 1-3 .019L5 15c-1.5-1.5-3-3.2-3-5.5\"/>","layers":"<path d=\"M12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83z\"/><path d=\"M2 12a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 12\"/><path d=\"M2 17a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 17\"/>","life-buoy":"<circle cx=\"12\" cy=\"12\" r=\"10\"/><path d=\"m4.93 4.93 4.24 4.24\"/><path d=\"m14.83 9.17 4.24-4.24\"/><path d=\"m14.83 14.83 4.24 4.24\"/><path d=\"m9.17 14.83-4.24 4.24\"/><circle cx=\"12\" cy=\"12\" r=\"4\"/>","lightbulb":"<path d=\"M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5\"/><path d=\"M9 18h6\"/><path d=\"M10 22h4\"/>","list-checks":"<path d=\"M13 5h8\"/><path d=\"M13 12h8\"/><path d=\"M13 19h8\"/><path d=\"m3 17 2 2 4-4\"/><path d=\"m3 7 2 2 4-4\"/>","mail":"<path d=\"m22 7-8.991 5.727a2 2 0 0 1-2.009 0L2 7\"/><rect x=\"2\" y=\"4\" width=\"20\" height=\"16\" rx=\"2\"/>","map-pin":"<path d=\"M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0\"/><circle cx=\"12\" cy=\"10\" r=\"3\"/>","megaphone":"<path d=\"M11 6a13 13 0 0 0 8.4-2.8A1 1 0 0 1 21 4v12a1 1 0 0 1-1.6.8A13 13 0 0 0 11 14H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2z\"/><path d=\"M6 14a12 12 0 0 0 2.4 7.2 2 2 0 0 0 3.2-2.4A8 8 0 0 1 10 14\"/><path d=\"M8 6v8\"/>","message-circle":"<path d=\"M2.992 16.342a2 2 0 0 1 .094 1.167l-1.065 3.29a1 1 0 0 0 1.236 1.168l3.413-.998a2 2 0 0 1 1.099.092 10 10 0 1 0-4.777-4.719\"/>","monitor-check":"<path d=\"m9 10 2 2 4-4\"/><rect width=\"20\" height=\"14\" x=\"2\" y=\"3\" rx=\"2\"/><path d=\"M12 17v4\"/><path d=\"M8 21h8\"/>","palette":"<path d=\"M12 22a1 1 0 0 1 0-20 10 9 0 0 1 10 9 5 5 0 0 1-5 5h-2.25a1.75 1.75 0 0 0-1.4 2.8l.3.4a1.75 1.75 0 0 1-1.4 2.8z\"/><circle cx=\"13.5\" cy=\"6.5\" r=\".5\" fill=\"currentColor\"/><circle cx=\"17.5\" cy=\"10.5\" r=\".5\" fill=\"currentColor\"/><circle cx=\"6.5\" cy=\"12.5\" r=\".5\" fill=\"currentColor\"/><circle cx=\"8.5\" cy=\"7.5\" r=\".5\" fill=\"currentColor\"/>","pencil":"<path d=\"M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z\"/><path d=\"m15 5 4 4\"/>","phone":"<path d=\"M13.832 16.568a1 1 0 0 0 1.213-.303l.355-.465A2 2 0 0 1 17 15h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2A18 18 0 0 1 2 4a2 2 0 0 1 2-2h3a2 2 0 0 1 2 2v3a2 2 0 0 1-.8 1.6l-.468.351a1 1 0 0 0-.292 1.233 14 14 0 0 0 6.392 6.384\"/>","play":"<path d=\"M5 5a2 2 0 0 1 3.008-1.728l11.997 6.998a2 2 0 0 1 .003 3.458l-12 7A2 2 0 0 1 5 19z\"/>","refresh-cw":"<path d=\"M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8\"/><path d=\"M21 3v5h-5\"/><path d=\"M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16\"/><path d=\"M8 16H3v5\"/>","rocket":"<path d=\"M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5\"/><path d=\"M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09\"/><path d=\"M9 12a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.4 22.4 0 0 1-4 2z\"/><path d=\"M9 12H4s.55-3.03 2-4c1.62-1.08 5 .05 5 .05\"/>","scale":"<path d=\"M12 3v18\"/><path d=\"m19 8 3 8a5 5 0 0 1-6 0zV7\"/><path d=\"M3 7h1a17 17 0 0 0 8-2 17 17 0 0 0 8 2h1\"/><path d=\"m5 8 3 8a5 5 0 0 1-6 0zV7\"/><path d=\"M7 21h10\"/>","scan-search":"<path d=\"M3 7V5a2 2 0 0 1 2-2h2\"/><path d=\"M17 3h2a2 2 0 0 1 2 2v2\"/><path d=\"M21 17v2a2 2 0 0 1-2 2h-2\"/><path d=\"M7 21H5a2 2 0 0 1-2-2v-2\"/><circle cx=\"12\" cy=\"12\" r=\"3\"/><path d=\"m16 16-1.9-1.9\"/>","search":"<path d=\"m21 21-4.34-4.34\"/><circle cx=\"11\" cy=\"11\" r=\"8\"/>","settings":"<path d=\"M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915\"/><circle cx=\"12\" cy=\"12\" r=\"3\"/>","share-2":"<circle cx=\"18\" cy=\"5\" r=\"3\"/><circle cx=\"6\" cy=\"12\" r=\"3\"/><circle cx=\"18\" cy=\"19\" r=\"3\"/><line x1=\"8.59\" x2=\"15.42\" y1=\"13.51\" y2=\"17.49\"/><line x1=\"15.41\" x2=\"8.59\" y1=\"6.51\" y2=\"10.49\"/>","shield-check":"<path d=\"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z\"/><path d=\"m9 12 2 2 4-4\"/>","shopping-cart":"<path d=\"m2.05 2.05 1.099-.028a1 1 0 0 1 1.008.815l2.69 14.347A1 1 0 0 0 7.83 18H18\"/><path d=\"M4.563 5h16.435a1 1 0 0 1 .981 1.204l-1.026 6.226A2 2 0 0 1 18.962 14H6.25\"/><circle cx=\"18\" cy=\"20\" r=\"2\"/><circle cx=\"8\" cy=\"20\" r=\"2\"/>","star":"<path d=\"M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z\"/>","target":"<circle cx=\"12\" cy=\"12\" r=\"10\"/><circle cx=\"12\" cy=\"12\" r=\"6\"/><circle cx=\"12\" cy=\"12\" r=\"2\"/>","trending-up":"<path d=\"M16 7h6v6\"/><path d=\"m22 7-8.5 8.5-5-5L2 17\"/>","truck":"<path d=\"M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2\"/><path d=\"M15 18H9\"/><path d=\"M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14\"/><circle cx=\"17\" cy=\"18\" r=\"2\"/><circle cx=\"7\" cy=\"18\" r=\"2\"/>","user-check":"<path d=\"m16 11 2 2 4-4\"/><path d=\"M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2\"/><circle cx=\"9\" cy=\"7\" r=\"4\"/>","users":"<path d=\"M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2\"/><path d=\"M16 3.128a4 4 0 0 1 0 7.744\"/><path d=\"M22 21v-2a4 4 0 0 0-3-3.87\"/><circle cx=\"9\" cy=\"7\" r=\"4\"/>","utensils":"<path d=\"M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2\"/><path d=\"M7 2v20\"/><path d=\"M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7\"/>","wallet":"<path d=\"M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1\"/><path d=\"M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4\"/>","wifi":"<path d=\"M12 20h.01\"/><path d=\"M2 8.82a15 15 0 0 1 20 0\"/><path d=\"M5 12.859a10 10 0 0 1 14 0\"/><path d=\"M8.5 16.429a5 5 0 0 1 7 0\"/>","wrench":"<path d=\"M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.106-3.105c.32-.322.863-.22.983.218a6 6 0 0 1-8.259 7.057l-7.91 7.91a1 1 0 0 1-2.999-3l7.91-7.91a6 6 0 0 1 7.057-8.259c.438.12.54.662.219.984z\"/>"}, RULES = [["email|subscribe|newsletter|unsubscribe|confirmation","mail"],["idea|brainstorm","lightbulb"],["moodboard|research|^concepts","palette"],["audit|inspect|search|find|discover|spot|identify|look|browse|explore","search"],["verify|check|confirm|validate|checksum|vet|reference","badge-check"],["review|assess|evaluate|bust","scan-search"],["test|try|testnet","list-checks"],["plan|brief|scope|outline|define|goal|budget|list|calendar|strategy|architect|decide|occasion|date|layout|criteria","clipboard-list"],["build|create|produce|develop|design|make|write|record|footage|generate|edit","hammer"],["install|set up|setup|configure|tool|customise|replace|swap|remove|firmware|patch|update|connect|point dns|harden","wrench"],["launch|publish|release|go live|rollout|staged|ship safely","rocket"],["learn|read|understand|know|guide|glossary|standard|rules|law|basics|facts|craft|concepts|guidelines|rights","book-open"],["deliver|delivery|ship|dispatch|fulfil|transport|pick up|pickup|wrap|send","truck"],["measure|monitor|report|analy|track|metric|watch|result|outcome|footprint|usage|data use","chart-no-axes-column"],["refine|improve|iterate|optimi|grow","trending-up"],["secure|security|safe|protect|privacy|firewall|ssh|vpn|isolat|essential eight|credential|password|key|incident","shield-check"],["pay|paid|price|cost|fees?([^a-z]|$)|funds|wallet|money|revenue|share is paid","wallet"],["compare|weigh|choose|pick|select|match|prefer|fit","scale"],["order|buy|shop|cart|purchase","shopping-cart"],["menu|venue|food|restaurant","utensils"],["meet|interview|video call|public place","users"],["chat|talk|ask|tell|contact|enquir|message|discuss|get in touch|call","message-circle"],["agree|offer|contract|hire|negotiat|terms|sign","handshake"],["support|help|quitline|gp|pharmacist|idcare|advis|insurer","life-buoy"],["feedback|honest|rate|review everything","star"],["hand over|handover|document|archive|evidence|logs|records|cite|source","file-text"],["download|zip|extension|npm","download"],["back up|backup|restore","hard-drive"],["notify|notification|alert|report anything|report problems|report to|flag","bell"],["wifi|wi-fi|wi‑fi|network|router|access point|mesh|backhaul|cable|nbn|coverage|connection","wifi"],["switch|keep your number|exit|return","refresh-cw"],["care|love|community|respect|pet|gift|person","heart"],["join|programme|register|onboard|sign up|account","user-check"],["start|first|enter|begin","flag"],["accessib|caption","eye"],["limit|boundar|quit|pause|slip|cravings|stop","target"],["separate|guest|iot|segment","shield-check"],["advertis|ads|sponsor|disclos","megaphone"],["complian","badge-check"],["fast|speed","gauge"],["park","map-pin"],["brand|colour|font","palette"],["train|teach|course","graduation-cap"],["pass it on|share","share-2"],["frequent|changes|automate","settings"],["diversif","layers"],["correct|error|fix","pencil"],["stream|redeem|code|play","play"],["minimi","target"]];
  var svg = function (n, cls) { return '<svg class="ico ' + (cls || '') + '" aria-hidden="true" focusable="false" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">' + (ICONS[n] || ICONS['circle-check-big']) + '</svg>'; };
  var small = matchMedia('(max-width: 768px)');
  var uid = 0, id = function (p) { return p + '-' + (++uid); };
  var topOffset = function () { var h = D.querySelector('header'); if (!h) return 0; var s = getComputedStyle(h); return (s.position === 'sticky' || s.position === 'fixed') ? Math.max(0, h.getBoundingClientRect().bottom) : 0; };

  /* 1. step icons + centred icon cards */
  var pick = function (t) { t = (t || '').toLowerCase(); for (var i = 0; i < RULES.length; i++) { if (new RegExp('(^|[^a-z])(' + RULES[i][0] + ')').test(t)) return RULES[i][1]; } return 'circle-check-big'; };
  $$('ul.steps, ol.steps').forEach(function (l) {
    if (l.classList.contains('mp-steps')) return; l.classList.add('mp-steps');
    $$(':scope > li', l).forEach(function (li) { if (li.querySelector('.mp-ico')) return; var s = D.createElement('span'); s.className = 'mp-ico'; s.setAttribute('aria-hidden', 'true'); s.innerHTML = svg(pick(li.textContent)); li.insertBefore(s, li.firstChild); });
  });
  $$('main article, main .card, main li').forEach(function (c) {
    if (c.closest('header,footer,nav,form,.steps,.timeline')) return;
    var a = c.firstElementChild, b = a && a.nextElementSibling; if (!a || !b || !/^H[2-4]$/.test(b.tagName)) return;
    var iconOnly = a.tagName.toLowerCase() === 'svg' || (a.children.length === 1 && a.firstElementChild.tagName.toLowerCase() === 'svg' && !a.textContent.trim());
    if (iconOnly) c.classList.add('mp-ic');
  });

  /* 2. footer link groups -> accordion on small screens */
  var fgroups = [];
  $$('footer h2, footer h3').forEach(function (h) {
    var p = h.nextElementSibling; if (!p || !/^(UL|OL|NAV|FORM|DIV|P)$/.test(p.tagName) || h.querySelector('.mp-fbtn')) return;
    if (p.tagName === 'DIV' && !p.querySelector('a,form')) return;
    var g = h.parentElement; g.classList.add('mp-fgroup'); p.classList.add('mp-fpanel'); if (!p.id) p.id = id('mp-fp');
    var b = D.createElement('button'); b.type = 'button'; b.className = 'mp-fbtn'; b.setAttribute('aria-controls', p.id);
    while (h.firstChild) b.appendChild(h.firstChild); b.insertAdjacentHTML('beforeend', svg('chevron', 'mp-chev').replace(ICONS['circle-check-big'], '<path d="m6 9 6 6 6-6"/>')); h.appendChild(b);
    b.addEventListener('click', function () { if (!small.matches) return; var open = b.getAttribute('aria-expanded') !== 'true'; b.setAttribute('aria-expanded', String(open)); p.classList.toggle('mp-closed', !open); });
    fgroups.push([b, p]);
  });
  var syncFooter = function () { fgroups.forEach(function (x) { if (small.matches) { var keep = x[1].contains(D.activeElement); x[0].removeAttribute('tabindex'); x[0].setAttribute('aria-expanded', String(keep)); x[1].classList.toggle('mp-closed', !keep); } else { x[0].setAttribute('tabindex', '-1'); x[0].removeAttribute('aria-expanded'); x[1].classList.remove('mp-closed'); } }); };
  syncFooter(); (small.addEventListener ? small.addEventListener('change', syncFooter) : small.addListener(syncFooter));

  /* 3. header dropdowns -> full-screen overlay on small screens */
  var drops = $$('header details').filter(function (d) { return !d.matches('.nc-mobile-menu,.lang') && d.querySelector(':scope > div, :scope > nav, :scope > ul'); });
  var lock = function () { H.classList.toggle('mp-lock', small.matches && drops.some(function (d) { return d.open; })); };
  drops.forEach(function (d) {
    var pnl = d.querySelector(':scope > div, :scope > nav, :scope > ul'), sum = d.querySelector('summary'); pnl.classList.add('mp-ov');
    var hd = D.createElement('div'); hd.className = 'mp-ovhead'; var t = D.createElement('span'); t.textContent = (sum.textContent || sum.getAttribute('aria-label') || 'Menu').trim();
    var cb = D.createElement('button'); cb.type = 'button'; cb.className = 'mp-ovclose'; cb.setAttribute('aria-label', 'Close ' + t.textContent + ' menu'); cb.innerHTML = svg('x').replace(ICONS['circle-check-big'], '<path d="M18 6 6 18M6 6l12 12"/>');
    hd.appendChild(t); hd.appendChild(cb); pnl.insertBefore(hd, pnl.firstChild);
    cb.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); if (d.open) sum.click(); if (d.open) d.open = false; sum.focus(); });
    d.addEventListener('toggle', function () { lock(); if (d.open && small.matches) setTimeout(function () { cb.focus({ preventScroll: true }); }, 30); });
    d.addEventListener('keydown', function (e) { if (e.key === 'Escape' && d.open) { d.open = false; sum.focus(); } });
  });
  (small.addEventListener ? small.addEventListener('change', lock) : small.addListener(lock));

  /* 4. Get a quote: header button (all viewports) + homepage hero CTA */
  var qa = $$('a[href]').filter(function (a) { var h = a.getAttribute('href'); return /quote/i.test(h) && !/^(https?:)?\/\//i.test(h) && !/^mailto:/i.test(h); });
  var pref = function (h) { return /request-quote/i.test(h) ? 0 : /quote(\/|\?|$)/i.test(h) ? 1 : 2; };
  qa.sort(function (x, y) { return pref(x.getAttribute('href')) - pref(y.getAttribute('href')); });
  var qhref = qa.length ? qa[0].getAttribute('href').split('?')[0] : null;
  var hdr = D.querySelector('body > header, header.top, header');
  if (qhref && hdr && !hdr.querySelector('.mp-quote')) {
    var q = D.createElement('a'); q.className = 'mp-quote'; q.href = qhref; q.innerHTML = svg('calculator').replace(ICONS['circle-check-big'], '<rect width="16" height="20" x="4" y="2" rx="2"/><path d="M8 6h8M16 14v4M16 10h.01M12 10h.01M8 10h.01M12 14h.01M8 14h.01M12 18h.01M8 18h.01"/>') + '<span>Get a quote</span>';
    var host = hdr.querySelector('.top-in') || hdr; host.classList.add('mp-qhost');
    var before = host.querySelector(':scope > .hdr-tools, :scope > .hdr-search, :scope > .theme-toggle, :scope > .icon-btn, :scope > details.lang, :scope > details.mnav');
    host.insertBefore(q, before || null);
    var path = location.pathname.replace(/index\.html$/, '');
    var hero = (path === '/' || path === '') && D.querySelector('main .hero .btns, main .hero-actions, main .hero .cta-actions');
    if (hero && !hero.querySelector('a[href*="quote"]')) { var hb = D.createElement('a'); var tpl = hero.querySelector('a'); hb.className = (tpl && /btn/.test(tpl.className)) ? 'btn alt mp-hero-quote' : 'secondary mp-hero-quote'; hb.href = qhref; hb.innerHTML = q.innerHTML; hero.appendChild(hb); }
  }

  /* 4b. header nav that overflows (brand overlapped) switches to the compact menu layout; only when the page has a compact menu */
  var top = D.querySelector('header.top .top-in'), mn = top && top.querySelector('.mnav'), nm = top && top.querySelector('nav.main');
  var fit = function () { if (!top || !mn || !nm) return; H.classList.remove('mp-navcompact'); if (getComputedStyle(nm).display === 'none') return; var br = top.querySelector('.brand'); var fc = nm.firstElementChild, nl = nm.getBoundingClientRect().left; var over = top.scrollWidth > top.clientWidth + 1 || nm.scrollWidth > nm.clientWidth + 1 || (fc && fc.getBoundingClientRect().left < nl - 1) || (br && fc && br.getBoundingClientRect().right > fc.getBoundingClientRect().left + 1); H.classList.toggle('mp-navcompact', over); };
  fit(); addEventListener('resize', fit); addEventListener('load', fit);

  /* 5. stepped form cards (every non-search form). Presentation only: fields, names, validation, spam traps and action are untouched. */
  var isSearch = function (f) { return f.getAttribute('role') === 'search' || /search/i.test(f.getAttribute('action') || '') || (f.querySelectorAll('input:not([type=hidden])').length === 1 && f.querySelector('input[type=search]')); };
  var userField = function (el) { return el.matches('input:not([type=hidden]):not([tabindex="-1"]),select,textarea') && !el.closest('[hidden]'); };
  $$('form').forEach(function (f) {
    if (isSearch(f) || f.classList.contains('mp-card')) return;
    f.classList.add('mp-card');
    if (f.querySelector('.step [data-ms-next], [data-ms-next]') || f.querySelector('fieldset.step')) { f.classList.add('mp-own-steps'); return; }
    var kids = [].slice.call(f.children).filter(function (k) { return !(k.tagName === 'INPUT' && k.type === 'hidden') && !k.hasAttribute('hidden') && !k.matches('.form-msg,.form-status,[role=status],[aria-live],script,template'); });
    var subEl = kids.filter(function (k) { return k.matches('[type=submit],button:not([type])') || k.querySelector('[type=submit],button:not([type])'); }).pop();
    var groups = kids.filter(function (k) { return k !== subEl; });
    if (!groups.length) return;
    var bar = D.createElement('div'); bar.className = 'mp-stepbar mp-off'; bar.innerHTML = '<span class="mp-stepn" aria-live="polite"></span><span class="mp-prog" aria-hidden="true"><i></i></span>';
    var nav = D.createElement('div'); nav.className = 'mp-fnav mp-off';
    var back = D.createElement('button'); back.type = 'button'; back.className = 'mp-back'; back.textContent = 'Back';
    var next = D.createElement('button'); next.type = 'button'; next.className = 'mp-next'; next.textContent = 'Next';
    nav.appendChild(back); nav.appendChild(next);
    f.insertBefore(bar, groups[0]); if (subEl) f.insertBefore(nav, subEl); else f.appendChild(nav);
    var steps = [[groups.slice()]][0], cur = 0, laidFor = '';
    var layout = function (force) {
      var key = innerWidth + 'x' + innerHeight; if (!force && key === laidFor) return; if (!f.getClientRects().length) return; laidFor = key;
      var keepEl = steps[cur] && steps[cur][0];
      groups.forEach(function (g) { g.classList.remove('mp-off'); }); bar.classList.add('mp-off'); nav.classList.add('mp-off'); if (subEl) subEl.classList.remove('mp-off');
      var budget = Math.max(220, innerHeight - topOffset() - 32 - 44 - 60 - 24);
      var total = f.getBoundingClientRect().height;
      if (total <= innerHeight - topOffset() - 16) { steps = [groups.slice()]; }
      else {
        steps = []; var s = [], top = null, subH = subEl ? subEl.getBoundingClientRect().height + 8 : 0;
        groups.forEach(function (g, i) { var r = g.getBoundingClientRect(); if (top === null) top = r.top; var last = i === groups.length - 1; var lim = budget - (last ? subH : 0);
          if (s.length && r.bottom - top > lim) { steps.push(s); s = []; top = r.top; } s.push(g); });
        if (s.length) steps.push(s);
      }
      cur = 0; if (keepEl) steps.forEach(function (s, i) { if (s.indexOf(keepEl) > -1) cur = i; });
      f.classList.toggle('mp-stepped', steps.length > 1); show(false);
    };
    var show = function (scroll) {
      var n = steps.length; groups.forEach(function (g) { g.classList.toggle('mp-off', steps[cur].indexOf(g) < 0); });
      bar.classList.toggle('mp-off', n < 2); nav.classList.toggle('mp-off', n < 2);
      bar.querySelector('.mp-stepn').textContent = 'Step ' + (cur + 1) + ' of ' + n; bar.querySelector('i').style.width = ((cur + 1) / n * 100) + '%';
      back.classList.toggle('mp-off', cur === 0); next.classList.toggle('mp-off', cur === n - 1); if (subEl) subEl.classList.toggle('mp-off', cur !== n - 1 && n > 1);
      if (scroll) { H.style.setProperty('--mp-top', topOffset() + 'px'); var r = f.getBoundingClientRect(); if (r.top < topOffset() || r.bottom > innerHeight) f.scrollIntoView({ block: 'start', behavior: 'instant' }); var fe = steps[cur].map(function (g) { return g.matches('input,select,textarea') ? g : g.querySelector('input:not([type=hidden]),select,textarea'); }).filter(Boolean)[0]; if (fe) try { fe.focus({ preventScroll: true }); } catch (e) {} }
    };
    var valid = function () { var bad = null; steps[cur].forEach(function (g) { [g].concat([].slice.call(g.querySelectorAll('input,select,textarea'))).forEach(function (el) { if (!bad && el.matches('input,select,textarea') && userField(el) && !el.checkValidity()) bad = el; }); }); if (bad) { bad.reportValidity(); try { bad.focus(); } catch (e) {} return false; } return true; };
    next.addEventListener('click', function () { if (valid() && cur < steps.length - 1) { cur++; show(true); } });
    back.addEventListener('click', function () { if (cur > 0) { cur--; show(true); } });
    f.addEventListener('submit', function (e) { if (steps.length > 1 && cur < steps.length - 1) { e.preventDefault(); e.stopImmediatePropagation(); next.click(); } }, true);
    f.addEventListener('reset', function () { setTimeout(function () { cur = 0; show(false); }, 0); });
    var t; addEventListener('resize', function () { clearTimeout(t); t = setTimeout(function () { layout(false); }, 150); });
    if (window.ResizeObserver) { var ro = new ResizeObserver(function () { if (!laidFor && f.getClientRects().length) layout(true); }); ro.observe(f); }
    layout(true);
  });
})();
/* ==== /mobile-pass 1.0 ==== */
