(function(){
const C = window.CAT_CFG, T = C.t, L = C.lang;
const $ = s => document.querySelector(s);
const grid = $('#catGrid'), countEl = $('#catCount'), fm = $('#fm'), fmBody = $('#fmBody');
const state = { cat:'', gender:'', sale:false, brand:'', frames:[] };

const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const money = n => Math.round(Number(n)||0).toLocaleString('sr-RS') + ' RSD';
// Vrednosti iz CRM-a su na srpskom; za druge jezike prevodimo poznate reči.
const tv = v => {
  if (!v) return '';
  if (L === 'sr') return v;
  return String(v).split('/').map(p => { const k = p.trim().toLowerCase(); return (C.dict[k] && C.dict[k][L]) || p.trim(); }).join(' / ');
};
const priceHtml = f => f.sale_price != null
  ? `<s>${money(f.price)}</s>${money(f.sale_price)}`
  : money(f.price);
const isSale = f => f.sale_price != null && Number(f.sale_price) < Number(f.price);
const pct = f => Math.round((1 - Number(f.sale_price) / Number(f.price)) * 100);
const label = f => f.sale_price == null ? '' :
  (f.discount_type === 'ucenjeno' ? T.l_ucenjeno : `${T.l_sale} −${pct(f)}%`);

async function load(){
  grid.innerHTML = `<p class="cat-msg">${esc(T.cat_loading)}</p>`;
  const cols = 'id,code,brand,model,gender,category,price,sale_price,discount_type,discount_reason,has_clip_on,material,color,size,sun_lens_type,sun_lens_material,polarized,uv_protection,filter_category,photos,desc_sr,desc_hu,desc_en,desc_ru';
  const url = `${C.url}/rest/v1/frames?select=${cols}&is_published=eq.true&is_sold=eq.false&deleted_at=is.null&order=sort_order.asc,created_at.desc`;
  try {
    const r = await fetch(url, { headers: { apikey: C.key } });
    if (!r.ok) throw new Error(r.status);
    state.frames = await r.json();
  } catch (e) {
    grid.innerHTML = `<p class="cat-msg">${esc(T.cat_error)}<a href="tel:${C.phoneTel}">${esc(C.phone)}</a></p>`;
    return;
  }
  const brands = [...new Set(state.frames.map(f => f.brand))].sort((a,b) => a.localeCompare(b));
  $('#fBrand').innerHTML = `<option value="">${esc(T.f_brand_all)}</option>` + brands.map(b => `<option>${esc(b)}</option>`).join('');
  render();
  openFromHash();
}

function filtered(){
  return state.frames.filter(f => {
    if (state.cat && f.category !== state.cat) return false;
    if (state.gender === 'zenski' && !['zenski','uniseks'].includes(f.gender)) return false;
    if (state.gender === 'muski' && !['muski','uniseks'].includes(f.gender)) return false;
    if (state.gender === 'deciji' && f.gender !== 'deciji') return false;
    if (state.sale && !isSale(f)) return false;
    if (state.brand && f.brand !== state.brand) return false;
    return true;
  });
}

function render(){
  const rows = filtered();
  countEl.textContent = rows.length ? `${rows.length} / ${state.frames.length}` : '';
  if (!rows.length) { grid.innerHTML = `<p class="cat-msg">${esc(T.cat_empty)}</p>`; return; }
  grid.innerHTML = rows.map(f => {
    const ph = f.photos && f.photos[0];
    const lab = label(f);
    return `<button type="button" class="fcard" data-id="${esc(f.id)}">
      <span class="fcard-ph">${ph ? `<img src="${esc(ph)}" alt="${esc(f.brand + ' ' + f.model)}" loading="lazy">` : ''}${lab ? `<span class="flabel">${esc(lab)}</span>` : ''}</span>
      <span class="fcard-txt">
        <span class="fcard-brand">${esc(f.brand)}</span>
        <span class="fcard-model">${esc(f.model)}${f.has_clip_on ? ' · ' + esc(T.l_clip) : ''}</span>
        <span class="price">${priceHtml(f)}</span>
      </span>
    </button>`;
  }).join('');
  grid.querySelectorAll('.fcard-ph img').forEach(softThumb);
}

// ── meke minijature za listu ──
// Fotografija se smanjuje u koracima po pola (svaki korak usrednjava piksele i guši zrno),
// pa se crta u nižoj rezoluciji od ekrana i blago omekšava. Otvorena kartica koristi original.
function softThumb(img){
  const box = img.parentElement;
  const draw = () => {
    const bw = box.clientWidth, bh = box.clientHeight;
    if (!bw || !bh || !img.naturalWidth) return;
    const k = Math.min(window.devicePixelRatio || 1, 1.25);
    const tw = Math.round(bw * k), th = Math.round(bh * k);
    // izrez kao object-fit: cover
    const sr = img.naturalWidth / img.naturalHeight, tr = tw / th;
    let sw = img.naturalWidth, sh = img.naturalHeight, sx = 0, sy = 0;
    if (sr > tr) { sw = sh * tr; sx = (img.naturalWidth - sw) / 2; } else { sh = sw / tr; sy = (img.naturalHeight - sh) / 2; }
    let src = img, cw = sw, ch = sh, first = true;
    while (cw / 2 >= tw * 1.15) {
      const c = document.createElement('canvas');
      c.width = Math.round(cw / 2); c.height = Math.round(ch / 2);
      const x = c.getContext('2d'); x.imageSmoothingEnabled = true; x.imageSmoothingQuality = 'high';
      if (first) x.drawImage(src, sx, sy, sw, sh, 0, 0, c.width, c.height);
      else x.drawImage(src, 0, 0, cw, ch, 0, 0, c.width, c.height);
      src = c; cw = c.width; ch = c.height; first = false;
    }
    let out = box.querySelector('canvas');
    if (!out) { out = document.createElement('canvas'); out.setAttribute('aria-hidden', 'true'); box.insertBefore(out, img.nextSibling); }
    out.width = tw; out.height = th;
    const x = out.getContext('2d'); x.imageSmoothingEnabled = true; x.imageSmoothingQuality = 'high';
    if ('filter' in x) x.filter = 'blur(0.6px)';
    if (first) x.drawImage(src, sx, sy, sw, sh, -1, -1, tw + 2, th + 2);
    else x.drawImage(src, 0, 0, cw, ch, -1, -1, tw + 2, th + 2);
    box.classList.add('soft');
  };
  if (img.complete && img.naturalWidth) draw(); else img.addEventListener('load', draw, { once: true });
  img._soft = draw;
}
let rsT;
addEventListener('resize', () => { clearTimeout(rsT); rsT = setTimeout(() => grid.querySelectorAll('.fcard-ph img').forEach(i => i._soft && i._soft()), 200); });

// ── filteri ──
document.querySelectorAll('[data-f]').forEach(b => b.addEventListener('click', () => {
  const k = b.dataset.f, v = b.dataset.v;
  if (k === 'sale') state.sale = !state.sale;
  else state[k] = state[k] === v ? '' : v;
  document.querySelectorAll('[data-f]').forEach(x => {
    const on = x.dataset.f === 'sale' ? state.sale : (x.dataset.v === '' ? state[x.dataset.f] === '' : state[x.dataset.f] === x.dataset.v);
    x.setAttribute('aria-pressed', on ? 'true' : 'false');
  });
  render();
}));
$('#fBrand').addEventListener('change', e => { state.brand = e.target.value; render(); });
grid.addEventListener('click', e => { const c = e.target.closest('.fcard'); if (c) openFrame(c.dataset.id); });

// ── detalj ──
function specRows(f){
  const r = [[T.s_code, esc(f.code)]];
  if (f.material) r.push([T.s_material, esc(tv(f.material))]);
  if (f.color) r.push([T.s_color, esc(tv(f.color))]);
  if (f.size) r.push([T.s_size, `${esc(f.size)}<small>${esc(T.s_size_hint)}</small>`]);
  if (f.category === 'suncani') {
    const lens = [tv(f.sun_lens_type), tv(f.sun_lens_material)].filter(Boolean).join(', ');
    if (lens) r.push([T.s_lens, esc(lens)]);
    if (f.polarized) r.push([T.s_polar, esc(T.s_yes)]);
    if (f.uv_protection) r.push([T.s_uv, esc(f.uv_protection)]);
    if (f.filter_category != null) r.push([T.s_filter, esc(f.filter_category)]);
  }
  if (f.has_clip_on) r.push([T.s_clip, esc(T.s_yes)]);
  return r.map(([k, v]) => `<tr><td>${esc(k)}</td><td>${v}</td></tr>`).join('');
}

function openFrame(id, push = true){
  const f = state.frames.find(x => x.id === id);
  if (!f) return;
  const photos = (f.photos || []).filter(Boolean);
  const desc = f['desc_' + L] || f.desc_sr || '';
  const kind = f.category === 'suncani' ? T.l_sun : T.l_optical;
  const lab = label(f);
  fmBody.innerHTML = `
    <div class="fm-grid">
      <div>
        <div class="fm-main">${photos[0] ? `<img id="fmImg" src="${esc(photos[0])}" alt="${esc(f.brand + ' ' + f.model)}"><span class="fm-zoom" aria-hidden="true"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5 21 21M10.5 7.5v6M7.5 10.5h6"/></svg></span>` : ''}${lab ? `<span class="flabel">${esc(lab)}</span>` : ''}</div>
        ${photos.length > 1 ? `<div class="fm-thumbs">${photos.map((p, i) => `<button type="button" data-src="${esc(p)}" aria-current="${i === 0}"><img src="${esc(p)}" alt="" loading="lazy"></button>`).join('')}</div>` : ''}
      </div>
      <div>
        <span class="kicker" style="margin-bottom:0">${esc(kind)}</span>
        <h2 id="fmTitle">${esc(f.brand)}<span class="fm-model">${esc(f.model)}</span></h2>
        <span class="price">${priceHtml(f)}</span>
        ${desc ? `<p class="fm-desc">${esc(desc)}</p>` : ''}
        ${f.discount_type === 'ucenjeno' && f.discount_reason ? `<p class="fm-reason">${esc(T.s_reason)}: ${esc(f.discount_reason)}</p>` : ''}
        <table class="spec">${specRows(f)}</table>
        <div class="rform" id="rbox">${formHtml(f)}</div>
      </div>
    </div>`;
  fmBody.querySelectorAll('.fm-thumbs button').forEach(b => b.addEventListener('click', () => {
    $('#fmImg').src = b.dataset.src;
    fmBody.querySelectorAll('.fm-thumbs button').forEach(x => x.setAttribute('aria-current', x === b));
  }));
  const mi = $('#fmImg');
  if (mi) mi.closest('.fm-main').addEventListener('click', () => openZoom(mi.src, mi.alt));
  bindForm(f);
  fm.classList.add('open'); document.body.classList.add('fm-open');
  fm.scrollTop = 0;
  if (push) history.replaceState(null, '', '#' + f.id);
  $('#fmClose').focus();
}

function closeFrame(){
  fm.classList.remove('open'); document.body.classList.remove('fm-open');
  history.replaceState(null, '', location.pathname + location.search);
}
$('#fmClose').addEventListener('click', closeFrame);
fm.addEventListener('click', e => { if (e.target === fm) closeFrame(); });
document.addEventListener('keydown', e => {
  if (e.key !== 'Escape') return;
  if (lb.classList.contains('open')) closeZoom();
  else if (fm.classList.contains('open')) closeFrame();
});
function openFromHash(){ const id = location.hash.slice(1); if (/^[0-9a-f-]{36}$/i.test(id)) openFrame(id, false); }

// ── uvećanje fotografije ──
const lb = document.createElement('div');
lb.className = 'lb';
lb.setAttribute('role', 'dialog'); lb.setAttribute('aria-modal', 'true');
lb.innerHTML = '<img alt="" draggable="false"><button type="button" class="lb-close" aria-label="Close">&times;</button>';
document.body.appendChild(lb);
const lbImg = lb.querySelector('img');
let z = 1, tx = 0, ty = 0;
const pts = new Map();
let gest = null;
const MAXZ = 5;
function clampT(){
  const w = lbImg.offsetWidth, h = lbImg.offsetHeight;
  const mx = Math.max(0, (w * z - innerWidth) / 2), my = Math.max(0, (h * z - innerHeight) / 2);
  tx = Math.min(mx, Math.max(-mx, tx)); ty = Math.min(my, Math.max(-my, ty));
}
function apply(anim){
  clampT();
  lbImg.style.transition = anim ? 'transform .25s ease' : 'none';
  lbImg.style.transform = `translate(${tx}px,${ty}px) scale(${z})`;
  lb.classList.toggle('zoomed', z > 1.01);
}
// zum oko tačke (px,py) ekrana
function zoomAt(nz, px, py, anim){
  nz = Math.min(MAXZ, Math.max(1, nz));
  const sx = px - innerWidth / 2, sy = py - innerHeight / 2;
  tx = sx - (sx - tx) * nz / z; ty = sy - (sy - ty) * nz / z;
  z = nz; if (z === 1) { tx = 0; ty = 0; }
  apply(anim);
}
function openZoom(src, alt){
  lbImg.src = src; lbImg.alt = alt || '';
  z = 1; tx = 0; ty = 0; apply();
  lb.classList.add('open');
  lb.querySelector('.lb-close').focus();
}
function closeZoom(){ lb.classList.remove('open'); pts.clear(); gest = null; }
lb.querySelector('.lb-close').addEventListener('click', closeZoom);
lb.addEventListener('wheel', e => { e.preventDefault(); zoomAt(z * Math.exp(-e.deltaY * 0.0025), e.clientX, e.clientY); }, { passive: false });
lb.addEventListener('pointerdown', e => {
  if (e.target.closest('.lb-close')) return;
  lb.setPointerCapture(e.pointerId);
  pts.set(e.pointerId, { x: e.clientX, y: e.clientY });
  if (pts.size === 1) gest = { mode: 'pan', x: e.clientX, y: e.clientY, tx, ty, moved: false, onImg: e.target === lbImg };
  else if (pts.size === 2) {
    const [a, b] = [...pts.values()];
    gest = { mode: 'pinch', d: Math.hypot(a.x - b.x, a.y - b.y), z, moved: true };
  }
});
lb.addEventListener('pointermove', e => {
  if (!pts.has(e.pointerId) || !gest) return;
  pts.set(e.pointerId, { x: e.clientX, y: e.clientY });
  if (gest.mode === 'pinch' && pts.size >= 2) {
    const [a, b] = [...pts.values()];
    const d = Math.hypot(a.x - b.x, a.y - b.y);
    zoomAt(gest.z * d / gest.d, (a.x + b.x) / 2, (a.y + b.y) / 2);
    gest.d = d; gest.z = z;
  } else if (gest.mode === 'pan') {
    const dx = e.clientX - gest.x, dy = e.clientY - gest.y;
    if (Math.abs(dx) + Math.abs(dy) > 6) gest.moved = true;
    if (gest.moved && z > 1) { tx = gest.tx + dx; ty = gest.ty + dy; apply(); }
  }
});
function endPtr(e){
  if (!pts.has(e.pointerId)) return;
  pts.delete(e.pointerId);
  if (gest && gest.mode === 'pan' && !gest.moved && e.type === 'pointerup') {
    if (z > 1.01) zoomAt(1, e.clientX, e.clientY, true);
    else if (gest.onImg) zoomAt(2.5, e.clientX, e.clientY, true);
    else closeZoom();
  }
  if (pts.size === 1) { const [p] = [...pts.values()]; gest = { mode: 'pan', x: p.x, y: p.y, tx, ty, moved: true }; }
  else if (!pts.size) gest = null;
}
lb.addEventListener('pointerup', endPtr);
lb.addEventListener('pointercancel', endPtr);
addEventListener('resize', () => { if (lb.classList.contains('open')) apply(); });

// ── rezervacija ──
function formHtml(f){
  return `
    <span class="kicker">${esc(T.r_kicker)}</span>
    <form id="rf" novalidate>
      <div class="rrow">
        <div class="rfield"><label class="f" for="rFirst">${esc(T.r_first)}</label><input type="text" id="rFirst" autocomplete="given-name" maxlength="60" required></div>
        <div class="rfield"><label class="f" for="rLast">${esc(T.r_last)}</label><input type="text" id="rLast" autocomplete="family-name" maxlength="60" required></div>
      </div>
      <div class="rfield"><label class="f" for="rPhone">${esc(T.r_phone)}</label><input type="tel" id="rPhone" autocomplete="tel" inputmode="tel" maxlength="30" placeholder="${esc(T.r_phone_ph)}" required></div>
      <div class="hp" aria-hidden="true"><label>Website<input type="text" id="rWeb" tabindex="-1" autocomplete="off"></label></div>
      <label class="rconsent"><input type="checkbox" id="rConsent"><span>${esc(T.r_consent)} <a href="${C.privacyUrl}" target="_blank">${esc(T.r_privacy)}</a>.</span></label>
      <button type="submit" class="btn-dark" id="rBtn">${esc(T.r_btn)}</button>
      <p class="rerr" id="rErr" role="alert" hidden></p>
      <p class="rnote">${esc(T.r_note)}</p>
    </form>`;
}

function bindForm(f){
  const form = $('#rf'), err = $('#rErr'), btn = $('#rBtn');
  const show = (msg, withPhone) => {
    err.innerHTML = esc(msg) + (withPhone ? `<a href="tel:${C.phoneTel}">${esc(C.phone)}</a>` : '');
    err.hidden = false;
  };
  form.addEventListener('input', () => { err.hidden = true; });
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const first = $('#rFirst').value.trim(), last = $('#rLast').value.trim(), phone = $('#rPhone').value.trim();
    const digits = phone.replace(/\D/g, '');
    if (!first || !last) return show(T.e_name);
    if (digits.length < 8 || digits.length > 15) return show(T.e_phone);
    if (!$('#rConsent').checked) return show(T.e_consent);
    btn.disabled = true;
    try {
      const r = await fetch(C.fn, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ frame_id: f.id, first_name: first, last_name: last, phone, lang: L, consent: true, website: $('#rWeb').value }),
      });
      const j = await r.json().catch(() => ({}));
      if (r.ok && j.ok) {
        $('#rbox').innerHTML = `<div class="rok"><h3>${esc(T.r_ok_h)}</h3><p>${esc(T.r_ok)}</p></div>`;
        return;
      }
      const code = j.error;
      if (code === 'name') show(T.e_name);
      else if (code === 'phone') show(T.e_phone);
      else if (code === 'consent') show(T.e_consent);
      else if (code === 'unavailable') show(T.e_unavailable);
      else if (code === 'rate') show(T.e_rate);
      else show(T.e_server, true);
    } catch (e2) {
      show(T.e_server, true);
    } finally {
      btn.disabled = false;
    }
  });
}

load();
})();
