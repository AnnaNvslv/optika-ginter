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
    if (state.sale && f.sale_price == null) return false;
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
      <span class="fcard-ph">${ph ? `<img src="${esc(ph)}" alt="${esc(f.brand + ' ' + f.model)}" loading="lazy">` : ''}</span>
      <span class="fcard-brand">${esc(f.brand)}</span>
      <span class="fcard-model">${esc(f.model)}${f.has_clip_on ? ' · ' + esc(T.l_clip) : ''}</span>
      <span class="price">${priceHtml(f)}</span>
      ${lab ? `<span class="flabel">${esc(lab)}</span>` : ''}
    </button>`;
  }).join('');
}

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
        <div class="fm-main">${photos[0] ? `<img id="fmImg" src="${esc(photos[0])}" alt="${esc(f.brand + ' ' + f.model)}">` : ''}</div>
        ${photos.length > 1 ? `<div class="fm-thumbs">${photos.map((p, i) => `<button type="button" data-src="${esc(p)}" aria-current="${i === 0}"><img src="${esc(p)}" alt="" loading="lazy"></button>`).join('')}</div>` : ''}
      </div>
      <div>
        <span class="kicker" style="margin-bottom:0">${esc(kind)}</span>
        <h2 id="fmTitle">${esc(f.brand)} ${esc(f.model)}</h2>
        <span class="price">${priceHtml(f)}</span>
        ${lab ? `<span class="flabel">${esc(lab)}</span>` : ''}
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
document.addEventListener('keydown', e => { if (e.key === 'Escape' && fm.classList.contains('open')) closeFrame(); });
function openFromHash(){ const id = location.hash.slice(1); if (/^[0-9a-f-]{36}$/i.test(id)) openFrame(id, false); }

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
