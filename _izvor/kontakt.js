(function(){
// Predporudžbina kontaktnih sočiva → Edge funkcija order-contact-lenses → CRM + Telegram
const C = window.KS_CFG, T = C.t, L = C.lang;
const $ = s => document.querySelector(s);
const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt = v => L === 'en' ? v : v.replace('.', ',');
const opts = (vals, show) => `<option value="">—</option>` + vals.map(v => `<option value="${esc(v)}">${esc(show ? show(v) : v)}</option>`).join('');
const AX = Array.from({length: 18}, (_, i) => String((i + 1) * 10));
const lensSel = $('#ksLens'), form = $('#ksForm'), err = $('#ksErr'), btn = $('#ksBtn');
const lens = () => C.lenses.find(l => l.id === lensSel.value);

function setLens(){
  const l = lens();
  form.classList.toggle('is-toric', !!(l && l.toric));
  $('#ksToric').hidden = !(l && l.toric);
  ['od', 'os'].forEach(e => {
    const f = n => form.querySelector(`[name=${e}_${n}]`);
    f('sph').innerHTML = opts(l ? l.sph_list : [], fmt);
    f('bc').innerHTML = opts(l ? l.bc : [], fmt);
    if (l && l.bc.length === 1) f('bc').value = l.bc[0];
    f('cyl').innerHTML = opts(l && l.toric ? l.cyl : [], fmt);
    f('ax').innerHTML = opts(l && l.toric ? AX : [], v => v + '°');
  });
  syncEyes();
}
function syncEyes(){
  form.querySelectorAll('.ks-eye').forEach(fs => {
    const off = fs.querySelector('[name$=_qty]').value === '0';
    fs.classList.toggle('is-off', off);
    fs.querySelectorAll('select:not([name$=_qty])').forEach(s => s.disabled = off);
  });
}
lensSel.addEventListener('change', setLens);
form.addEventListener('change', e => { if (/_qty$/.test(e.target.name)) syncEyes(); });
form.addEventListener('input', () => { err.hidden = true; });

// «Poruči» na kartici → izbor sočiva u formi
document.querySelectorAll('[data-pick]').forEach(b => b.addEventListener('click', () => {
  lensSel.value = b.dataset.pick; setLens();
  $('#porudzbina').scrollIntoView({ behavior: 'smooth' });
}));
const want = new URLSearchParams(location.search).get('sociva');
if (want && C.lenses.some(l => l.id === want)) { lensSel.value = want; }
setLens();

const show = (msg, withPhone) => {
  err.innerHTML = esc(msg) + (withPhone ? `<a href="tel:${C.phoneTel}">${esc(C.phone)}</a>` : '');
  err.hidden = false;
};
form.addEventListener('submit', async e => {
  e.preventDefault();
  const l = lens(), v = n => (form.querySelector(`[name=${n}]`).value || '').trim();
  if (!l) return show(T.e_lens);
  const eyes = {};
  for (const k of ['od', 'os']) {
    const qty = Number(v(k + '_qty'));
    if (!qty) continue;
    const eye = { qty, sph: v(k + '_sph'), bc: v(k + '_bc') };
    if (!eye.sph || !eye.bc) return show(T.e_params);
    if (l.toric) { eye.cyl = v(k + '_cyl'); eye.ax = v(k + '_ax'); if (!eye.cyl || !eye.ax) return show(T.e_toric); }
    eyes[k] = eye;
  }
  if (!Object.keys(eyes).length) return show(T.e_eye);
  const name = v('name'), phone = v('phone'), digits = phone.replace(/\D/g, '');
  if (!name) return show(T.e_name);
  if (digits.length < 8 || digits.length > 15) return show(T.e_phone);
  if (!$('#ksConsent').checked) return show(T.e_consent);
  btn.disabled = true;
  try {
    const r = await fetch(C.fn, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lens_id: l.id, lens_name: `${l.brand} ${l.name}`, toric: !!l.toric, od: eyes.od || null, os: eyes.os || null,
        name, phone, email: v('email'), comment: v('comment'), lang: L, consent: true, website: v('website') }),
    });
    const j = await r.json().catch(() => ({}));
    if (r.ok && j.ok) {
      $('#ksBox').innerHTML = `<div class="rok"><h3>${esc(T.ok_h)}</h3><p>${esc(T.ok)}</p></div>`;
      return;
    }
    if (j.error === 'phone') show(T.e_phone);
    else if (j.error === 'name') show(T.e_name);
    else if (j.error === 'rate') show(T.e_rate);
    else show(T.e_server, true);
  } catch (e2) {
    show(T.e_server, true);
  } finally {
    btn.disabled = false;
  }
});
})();
