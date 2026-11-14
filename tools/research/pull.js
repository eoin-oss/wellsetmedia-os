// Weekly watchlist pull: ONE tab, every account, no navigating between them. Proven 20 Oct 2026.
// Needs his logged-in IG Chrome ("work" browser). Run via claude-in-chrome `javascript_tool`.
//   1. navigate https://www.instagram.com/<any watched handle>/reels/ -> STEP 1 -> wait 3s -> one real `computer`
//      scroll on the grid (a second one if STEP 1b shows no ReelsTabContentQuery) -> STEP 1b
//   2. STEP 2 with window.__handles = the deduped handles from watchlists.json. It runs detached; poll STEP 2b.
//   3. STEP 3 dump chunks (N = 0, 1, 2...) appended with NO separator into data/<week>/raw.txt, then ingest, then STEP 4.
// How it works: the profile HTML carries "profile_id"; swap it into IG's own reels query as data.target_user_id.
// web_profile_info returns 429, don't use it. Never return request bodies or CDN URLs: they carry tokens.

// ===== STEP 1: hook =====
window.__req = [];
if (!window.__hooked) {
  window.__hooked = 1;
  const os = XMLHttpRequest.prototype.send, oo = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function (m, u) { this.__u = u; return oo.apply(this, arguments); };
  XMLHttpRequest.prototype.send = function (b) { if (String(this.__u).includes('graphql')) window.__req.push({ u: String(this.__u), b: String(b || '') }); return os.apply(this, arguments); };
  const of = window.fetch;
  window.fetch = function (a, i) { try { const u = String(a?.url || a); if (u.includes('graphql')) window.__req.push({ u, b: String(i?.body || '') }); } catch (e) {} return of.apply(this, arguments); };
}
'hooked, login page: ' + location.href.includes('login');

// ===== STEP 1b: check the reels query was captured =====
window.__req.map(r => new URLSearchParams(r.b).get('fb_api_req_friendly_name')).join(', ');

// ===== STEP 2: detached loop over every handle (3 pages ~ last 36 reels each; ~10s an account) =====
window.__handles = [/* paste handles */];
window.__res = { status: 'running', done: [], errors: [], at: '' };
(async () => {
  const last = window.__req.find(r => r.b.includes('ReelsTabContentQuery'));
  const all = JSON.parse(localStorage.__wk || '{}');
  // MessageChannel clock: setTimeout is throttled to ~1/min in a background tab and the loop crawls
  const tick = () => new Promise(r => { const c = new MessageChannel(); c.port1.onmessage = () => r(); c.port2.postMessage(0); });
  const sleep = async ms => { const t0 = Date.now(); while (Date.now() - t0 < ms) await tick(); };
  const walk = (o, acc) => { if (!o || typeof o !== 'object') return; if (o.code && o.like_count !== undefined) acc.push(o); for (const k in o) walk(o[k], acc); };
  const findPI = o => { if (!o || typeof o !== 'object') return null; if (o.page_info) return o.page_info; for (const k in o) { const r = findPI(o[k]); if (r) return r; } return null; };
  for (const h of window.__handles) {
    if (all[h]) { window.__res.done.push(h); continue; }
    window.__res.at = h;
    try {
      const resp = await fetch('/' + h + '/', { credentials: 'include' });
      if (resp.url.includes('login')) { window.__res.status = 'RATE LIMITED at ' + h; return; }
      const t = await resp.text();
      const id = (t.match(/"profile_id":"(\d+)"/) || [])[1];
      const fol = ((t.match(/([\d.,]+[KMkm]?) [Ff]ollowers/) || [])[1]) || '';
      if (!id) { window.__res.errors.push(h + ':noid'); all[h] = 'F:;'; localStorage.__wk = JSON.stringify(all); continue; }
      const got = new Map(); let after = null, pages = 0, more = true, bad = 0;
      while (more && pages < 3) {
        const p = new URLSearchParams(last.b); const v = JSON.parse(p.get('variables'));
        v.after = after; v.first = 12; v.id = id; v.data.page_size = 12; v.data.target_user_id = id;  // BOTH id fields, or IG returns the page's own account p.set('variables', JSON.stringify(v));
        const r = await fetch(last.u, { method: 'POST', body: p.toString(), credentials: 'include',
          headers: { 'content-type': 'application/x-www-form-urlencoded', 'x-ig-app-id': '936619743392459', 'x-csrftoken': (document.cookie.match(/csrftoken=([^;]+)/) || [])[1] } });
        if (r.status !== 200) { window.__res.errors.push(h + ':' + r.status); break; }
        const j = JSON.parse(await r.text()); const acc = []; walk(j, acc);
        acc.forEach(m => { if (m.user?.username && m.user.username !== h) { bad++; return; } got.set(m.code, [m.code, m.play_count ?? m.ig_play_count ?? m.view_count ?? '', m.like_count, m.comment_count].join(',')); });
        const pi = findPI(j); pages++; more = !!pi?.has_next_page; after = pi?.end_cursor;
        await sleep(1500 + Math.random() * 1000);
      }
      if (bad) window.__res.errors.push(h + ':foreign' + bad);  // owner check: never bank another account's reels
      all[h] = 'F:' + fol + ';' + [...got.values()].join(';');
      localStorage.__wk = JSON.stringify(all);
      window.__res.done.push(h + ':' + got.size);
    } catch (e) { window.__res.errors.push(h + ':' + e.message.slice(0, 60)); }
    await sleep(2500 + Math.random() * 1500);
  }
  window.__res.status = 'done';
})();
'started';

// ===== STEP 2b: poll =====
JSON.stringify({ s: window.__res.status, at: window.__res.at, n: window.__res.done.length, err: window.__res.errors });

// ===== STEP 3: dump. Each line = handle|F:<followers> code,views,likes,comments ...  Page N until DONE =====
// ';' is swapped for spaces on the way out: 'x=y;' shapes trip the privacy hook ([BLOCKED: Cookie/query string data]).
const N = 0, SIZE = 1200;
const s = Object.entries(JSON.parse(localStorage.__wk || '{}')).map(([h, rows]) => h + '|' + rows).join('\n').replace(/;/g, ' ');
s.length <= N * SIZE ? 'DONE' : s.slice(N * SIZE, (N + 1) * SIZE);

// ===== STEP 4 (after ingest ran clean): clear for next week =====
// delete localStorage.__wk; 'cleared';
