// Instagram reels pull, run via claude-in-chrome `javascript_tool` on https://www.instagram.com/<handle>/reels/
// Never return request bodies or CDN URLs from these calls: they carry tokens and the tool output gets blocked.

// ===== STEP 1: hook (run once, then do ONE real `computer` scroll so IG fires its own pagination query) =====
window.__req = window.__req || [];
if (!window.__hooked) {
  window.__hooked = 1;
  const os = XMLHttpRequest.prototype.send, oo = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function (m, u) { this.__u = u; return oo.apply(this, arguments); };
  XMLHttpRequest.prototype.send = function (b) {
    if (String(this.__u).includes('graphql')) window.__req.push({ u: String(this.__u), b: String(b || '') });
    return os.apply(this, arguments);
  };
  const of = window.fetch;
  window.fetch = function (a, i) {
    try { const u = String(a?.url || a); if (u.includes('graphql')) window.__req.push({ u, b: String(i?.body || '') }); } catch (e) {}
    return of.apply(this, arguments);
  };
}
'hooked';

// ===== STEP 2: replay IG's own reels query, page by page. Loops ~38s per call; call again until more=false =====
const last = window.__req[window.__req.length - 1];          // PolarisProfileReelsTabContentQuery_connection
window.__all = window.__all || new Map();
window.__st = window.__st || { after: null, pages: 0, more: true };
const walk = (o, acc) => { if (!o || typeof o !== 'object') return; if (o.code && o.like_count !== undefined) acc.push(o); for (const k in o) walk(o[k], acc); };
const findPI = o => { if (!o || typeof o !== 'object') return null; if (o.page_info) return o.page_info; for (const k in o) { const r = findPI(o[k]); if (r) return r; } return null; };
const t0 = Date.now();
while (window.__st.more && Date.now() - t0 < 38000) {
  const p = new URLSearchParams(last.b); const v = JSON.parse(p.get('variables'));
  v.after = window.__st.after; v.first = 12; if (v.data) v.data.page_size = 12; p.set('variables', JSON.stringify(v));
  const r = await fetch(last.u, { method: 'POST', body: p.toString(), credentials: 'include',
    headers: { 'content-type': 'application/x-www-form-urlencoded', 'x-ig-app-id': '936619743392459',
               'x-csrftoken': (document.cookie.match(/csrftoken=([^;]+)/) || [])[1] } });
  const j = JSON.parse(await r.text()); const acc = []; walk(j, acc);
  acc.forEach(m => window.__all.set(m.code, { code: m.code, views: m.play_count ?? m.ig_play_count ?? m.view_count ?? null, likes: m.like_count, com: m.comment_count }));
  const pi = findPI(j); window.__st.pages++; window.__st.more = !!pi?.has_next_page; window.__st.after = pi?.end_cursor;
  await new Promise(r => setTimeout(r, 700));
}
JSON.stringify({ pages: window.__st.pages, more: window.__st.more, total: window.__all.size });

// ===== STEP 3: dump in chunks of 35 (tool output truncates ~1.3K chars). Paste every chunk into data/ig_raw.txt =====
[...window.__all.values()].slice(0, 35).map(r => [r.code, r.views, r.likes, r.com].join(',')).join(';')
