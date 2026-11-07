# Сборка сайта: python3 build.py  -> папка OUT (4 языка + img + sitemap)
import json, os, re, shutil, urllib.parse, html as H
from content import *
from catalog_content import CAT, PRIV, VALUE_DICT
from stellest_content import ST, st_prices, ST_PRICE
from varilux_content import VX, vx_prices

DOMAIN = "https://optikaginter.rs"
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(BASE)  # корень репозитория
IMG_V = "9"  # менять при замене фото, чтобы браузер не брал старые
ASSET_V = "17"  # менять при изменении base.css или логотипов (папка assets/)
LANGS = ["sr", "hu", "en", "ru"]
PATH = {"sr": "/", "hu": "/hu/", "en": "/en/", "ru": "/ru/"}
ROOT = {"sr": "", "hu": "../", "en": "../", "ru": "../"}
LOCALE = {"sr": "sr_RS", "hu": "hu_HU", "en": "en_US", "ru": "ru_RU"}
ALT = {
    "sr": ("Enterijer Optike Ginter na Trgu Republike u Novom Sadu", "fotografija"),
    "hu": ("Az Optika Ginter üzletbelseje Újvidéken", "fotó"),
    "en": ("Inside Optika Ginter on Trg Republike, Novi Sad", "photo"),
    "ru": ("Интерьер Optika Ginter на площади Республики в Нови-Саде", "фото"),
}

P = json.load(open(f"{BASE}/paths.json"))
def ar(vb):
    _, _, w, h = map(float, vb.split()); return f"{w:.2f}/{h:.2f}"
STYLE = open(f"{BASE}/base.css", encoding="utf-8").read()
TPL = open(f"{BASE}/page.html", encoding="utf-8").read()
SUB_TPL = open(f"{BASE}/sub.html", encoding="utf-8").read()
CAT_CSS = open(f"{BASE}/catalog.css", encoding="utf-8").read()
CAT_JS = open(f"{BASE}/catalog.js", encoding="utf-8").read()
# Katalog čita javne okvire iz Ginter CRM (Supabase, samo objavljeni modeli — RLS),
# a rezervaciju šalje Edge funkciji reserve-frame (sajt nema pristup bazi).
SUPA_URL = "https://flxewreibnkyfoccfjtg.supabase.co"
SUPA_KEY = "sb_publishable_GtVx_U91nCREZ-fq4yfLLw_NLsvQYGQ"
SUB_PAGES = ["okviri", "privatnost", "stellest", "progresivne-naocare"]
fav = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{P["logo-og"]["vb"]}"><path d="{P["logo-og"]["d"]}"/></svg>'
# Zajednički fajlovi (assets/): stil, logotipi i favicon se učitavaju jednom i keširaju,
# umesto da se ugrađuju u svaku stranicu.
SPRITE = '<svg xmlns="http://www.w3.org/2000/svg">' + "".join(
    f'<symbol id="{sid}" viewBox="{P[n]["vb"]}"><path d="{P[n]["d"]}"/></symbol>'
    for sid, n in [("lg-full", "logo-full"), ("lg-og", "logo-og"), ("lg-hz", "logo-horizontal")]) + "</svg>"
SITE_CSS = re.sub(r"^\s*<style>\s*|\s*</style>\s*$", "", STYLE)

def services(d, extra=()):
    out = []
    items = list(d["services"]); items[3:3] = list(extra[1:]); items[6:6] = list(extra[:1])
    for i, (t, price, txt) in enumerate(items):
        op = " open" if i == 0 else ""
        pr = f'<span class="acc-price">{price}</span>' if price else ""
        out.append(f'      <div class="acc-item{op}"><button class="acc-btn" aria-expanded="{"true" if op else "false"}"><h3 class="acc-title">{t}</h3>{pr}<span class="acc-icon"></span></button>\n        <div class="acc-panel"><div class="acc-panel-in">{txt}</div></div></div>')
    return "\n".join(out)

def faq(d):
    return "\n".join(
        f'      <div class="acc-item"><button class="acc-btn" aria-expanded="false"><h3 class="acc-title">{q}</h3><span class="acc-icon"></span></button>\n        <div class="acc-panel"><div class="acc-panel-in">{a}</div></div></div>'
        for q, a in d["faq"])

def why(d):
    return "\n".join(f'      <div class="why-item"><span class="why-mark"></span><h3>{t}</h3><p>{p}</p></div>' for t, p in d["why"])

def team(d, root, photo_word):
    out = []
    for key, name, role, txt in d["team"]:
        if os.path.exists(f"{OUT}/img/{key}-600.webp"):
            media = f'<div class="ph photo"><div class="ph-inner"><img src="{root}img/{key}-600.webp" srcset="{root}img/{key}-600.webp 600w, {root}img/{key}-1000.webp 1000w" sizes="(min-width:760px) 33vw, 100vw" alt="{name} — Optika Ginter" loading="lazy" style="object-position:50% 25%"></div><div class="ph-corners"><i></i></div></div>'
        else:
            media = f'<div class="ph"><div class="ph-inner"></div><div class="ph-corners"><i></i></div><span class="ph-label">{d["ph_photo"]}</span></div>'
        out.append(f'      <article class="member reveal">{media}<h3>{name}</h3><div class="owner-role">{role}</div><p>{txt}</p></article>')
    return "\n".join(out)

def schema(lang, d):
    return json.dumps({
        "@context": "https://schema.org", "@type": "Optician",
        "name": "Optika Ginter", "url": DOMAIN + PATH[lang], "image": DOMAIN + "/img/og-image.jpg",
        "logo": DOMAIN + "/img/og-image.jpg",
        "telephone": PHONE_TEL, "email": EMAIL, "foundingDate": "2019", "priceRange": "RSD",
        "description": d["desc"],
        "address": {"@type": "PostalAddress", "streetAddress": ADDRESS, "addressLocality": "Novi Sad", "postalCode": "21000", "addressCountry": "RS"},
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "09:00", "closes": "20:00"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "09:00", "closes": "14:00"}],
        "paymentAccepted": "Cash, Credit Card", "currenciesAccepted": "RSD",
        "knowsLanguage": ["sr", "hu", "en", "ru"],
        "brand": [{"@type": "Brand", "name": b} for b in FRAMES],
        "sameAs": [INSTAGRAM],
    }, ensure_ascii=False)

def faq_schema(d):
    return json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in d["faq"]]}, ensure_ascii=False)

def head_seo(lang, d):
    alts = "\n".join(f'<link rel="alternate" hreflang="{l}" href="{DOMAIN}{PATH[l]}">' for l in LANGS)
    return f"""<link rel="canonical" href="{DOMAIN}{PATH[lang]}">
{alts}
<link rel="alternate" hreflang="x-default" href="{DOMAIN}/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Optika Ginter">
<meta property="og:title" content="{H.escape(d['title'])}">
<meta property="og:description" content="{H.escape(d['desc'])}">
<meta property="og:url" content="{DOMAIN}{PATH[lang]}">
<meta property="og:image" content="{DOMAIN}/img/og-image.jpg">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:locale" content="{LOCALE[lang]}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#12100D">"""

def lang_switch(lang, root, slug=""):
    sw = "".join(f'<a href="{(root + PATH[l].lstrip("/") + (slug + "/" if slug else "")) or "./"}" hreflang="{l}" lang="{l}"' + (' class="active" aria-current="page"' if l == lang else "") + f">{l.upper()}</a>" for l in LANGS)
    return f'<nav class="lang" aria-label="Language">{sw}</nav>'

def render(tpl, v):
    out = tpl
    for _ in range(2):
        out = re.sub(r"\{\{(\w+)\}\}", lambda m: v.get(m.group(1), m.group(0)), out)
    out = re.sub(r"(img/[\w-]+\.(?:webp|jpg))", r"\1?v=" + IMG_V, out)
    missing = set(re.findall(r"\{\{(\w+)\}\}", out))
    assert not missing, missing
    return out

def asset_vars(root):
    a = f"{root}assets/"
    return {"STYLE": f'<link rel="stylesheet" href="{a}site.css?v={ASSET_V}">',
            "FAVICON": f"{a}favicon.svg?v={ASSET_V}", "SPRITE": f"{a}logos.svg?v={ASSET_V}",
            "SUB_CSS_LINK": f'<link rel="stylesheet" href="{a}catalog.css?v={ASSET_V}">'}

def base_vars(lang):
    d = {**C[lang], **CAT[lang]}
    v = {k: x for k, x in d.items() if isinstance(x, str)}
    v.update({"lang": lang,
        "PHONE_DISPLAY": PHONE_DISPLAY, "PHONE_TEL": PHONE_TEL, "EMAIL": EMAIL, "INSTAGRAM": INSTAGRAM,
        "INSTAGRAM_HANDLE": INSTAGRAM_HANDLE, "ADDRESS": ADDRESS, "CITY": CITY, "PIB": PIB, "MB": MB})
    for k, n in {"FULL": "logo-full", "OG": "logo-og", "HZ": "logo-horizontal"}.items():
        v["VB_" + k] = P[n]["vb"]; v["D_" + k] = P[n]["d"]; v["AR_" + k] = ar(P[n]["vb"])
    return d, v

BRAND_DIR = os.path.join(OUT, "img", "brands")
def brand_slug(b):
    return re.sub(r"[^a-z0-9]+", "-", b.lower()).strip("-")

def brand_tile(b, root, href=None):
    """Pločica brenda: logo iz img/brands/<slug>.svg|png|webp ako postoji, inače naziv.
    Sa href — link (okviri → katalog filtriran po brendu)."""
    slug = brand_slug(b); inner = H.escape(b); cls = "brand-tile"
    for ext in ("svg", "png", "webp"):
        if os.path.exists(os.path.join(BRAND_DIR, f"{slug}.{ext}")):
            inner = f'<img src="{root}img/brands/{slug}.{ext}?v={IMG_V}" alt="{H.escape(b)}" loading="lazy">'
            cls += " has-logo"; break
    if href:
        return f'<a class="{cls}" href="{href}">{inner}</a>'
    return f'<span class="{cls}">{inner}</span>'

def build(lang):
    d, v = base_vars(lang); root = ROOT[lang]
    v.update({
        **asset_vars(root), "ROOT": root, "HOME": root or "./", "FRAMES_URL": "okviri/", "PRIVACY_URL": "privatnost/",
        "HEAD_SEO": head_seo(lang, d), "SCHEMA": schema(lang, d), "FAQ_SCHEMA": faq_schema(d),
        "LANG_SWITCH": lang_switch(lang, root),
        "SERVICES": services(d, [stellest_service(lang), vx_service(lang)]), "STELLEST_URL": "stellest/", "VX_URL": "progresivne-naocare/", "FAQ": faq(d), "WHY": why(d), "TEAM": team(d, root, ALT[lang][1]),
        "FRAMES": "".join(brand_tile(b, root, "okviri/?brend=" + urllib.parse.quote(b)) for b in FRAMES),
        "LENSES": "".join(brand_tile(b, root) for b in LENSES),
        "alt_salon": ALT[lang][0], "H1": d["title"].split(" | ")[0],
    })
    return render(TPL, v)

def stellest_service(lang):
    t = ST[lang]
    return (t["svc_title"], t["svc_price"], f'{t["svc_text"]} <a class="link-gold" href="stellest/">{t["svc_more"]} →</a>')

def sub_seo(lang, slug, title, desc, img="og-image.jpg"):
    url = lambda l: f"{DOMAIN}{PATH[l]}{slug}/"
    alts = "\n".join(f'<link rel="alternate" hreflang="{l}" href="{url(l)}">' for l in LANGS)
    return f"""<link rel="canonical" href="{url(lang)}">
{alts}
<link rel="alternate" hreflang="x-default" href="{url('sr')}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Optika Ginter">
<meta property="og:title" content="{H.escape(title)}">
<meta property="og:description" content="{H.escape(desc)}">
<meta property="og:url" content="{url(lang)}">
<meta property="og:image" content="{DOMAIN}/img/{img}">
<meta property="og:locale" content="{LOCALE[lang]}">
<meta name="theme-color" content="#12100D">"""

ST_CSS = """<style>
.st-top{ padding-bottom:72px; }
.st-hero{ display:grid; gap:48px; align-items:center; }
@media(min-width:960px){ .st-hero{ grid-template-columns:1fr 1fr; gap:80px; } }
.st-hero .lead{ max-width:560px; }
.st-badge{ display:inline-block; margin-top:28px; padding:9px 18px; border:1px solid var(--gold); color:var(--gold-deep); font-size:12px; letter-spacing:.22em; text-transform:uppercase; font-weight:500; }
.st-btns{ display:flex; flex-wrap:wrap; gap:14px; margin-top:30px; }
.st-btns .btn.dark{ background:var(--black); color:var(--gold-light); border-color:var(--black); }
.st-btns .btn.dark::before{ background:var(--gold-light); }
.st-btns .btn.dark:hover{ color:var(--black); }
.st-frame{ position:relative; }
.st-frame::before{ content:''; position:absolute; inset:18px -18px -18px 18px; border:1px solid var(--gold); z-index:0; }
.st-frame img,.st-frame video{ position:relative; z-index:1; display:block; width:100%; height:auto; }
.st-text{ max-width:760px; }
.st-text p{ color:var(--ink-soft); font-size:17px; margin-top:22px; }
.st-panel{ background:var(--panel); }
.st-stat{ display:grid; gap:56px; align-items:center; }
@media(min-width:960px){ .st-stat{ grid-template-columns:.9fr 1.1fr; gap:90px; } }
.st-num{ font-family:var(--serif); font-size:clamp(84px,12vw,150px); line-height:1; color:var(--gold-deep); }
.st-num-t{ color:var(--ink-soft); font-size:17px; max-width:460px; margin-top:14px; }
.st-list{ list-style:none; margin-top:34px; border-top:1px solid var(--gold); }
.st-list li{ position:relative; padding:20px 0 20px 64px; border-bottom:1px solid var(--line); color:var(--ink-soft); }
.st-list li::before{ content:''; position:absolute; left:0; top:33px; width:40px; height:1px; background:var(--gold); }
.st-list li b{ display:block; font-family:var(--serif); font-weight:400; font-size:24px; color:var(--ink); margin-bottom:4px; }
.st-price{ margin-top:40px; border-top:1px solid var(--gold); }
.st-prow{ display:grid; gap:14px 40px; padding:30px 0; border-bottom:1px solid var(--line); }
@media(min-width:900px){ .st-prow{ grid-template-columns:1.3fr 1fr 1fr; align-items:baseline; } }
.st-prow h3{ font-size:28px; }
.st-prow p{ color:var(--ink-faint); font-size:14px; margin-top:6px; }
.st-pl{ display:block; font-size:11px; letter-spacing:.2em; text-transform:uppercase; color:var(--ink-faint); margin-bottom:4px; }
.st-old{ font-family:var(--serif); font-size:24px; color:var(--ink-faint); text-decoration:line-through; text-decoration-thickness:1px; }
.st-new{ font-family:var(--serif); font-size:34px; color:var(--gold-deep); line-height:1.1; }
.st-pair{ display:block; color:var(--ink-soft); font-size:14px; margin-top:4px; }
.st-note{ color:var(--ink-faint); font-size:14px; margin-top:24px; max-width:760px; }
.st-tips{ display:grid; gap:0; margin-top:40px; border-top:1px solid var(--gold); }
@media(min-width:760px){ .st-tips{ grid-template-columns:repeat(2,1fr); } }
@media(min-width:1100px){ .st-tips{ grid-template-columns:repeat(4,1fr); } }
.st-tip{ padding:30px 28px 34px 0; border-bottom:1px solid var(--line); }
.st-tip .why-mark{ width:40px; height:1px; background:var(--gold); margin-bottom:22px; }
.st-tip h3{ font-size:24px; margin-bottom:10px; }
.st-tip p{ color:var(--ink-soft); font-size:15px; }
.st-video{ max-width:980px; margin:44px auto 0; }
.st-faq .accordion{ margin-top:40px; }
.st-faq .acc-title{ font-size:clamp(20px,2.4vw,28px); }
.st-cta{ background:var(--black); color:var(--white); text-align:center; }
.st-cta .h-sec em{ color:var(--gold-light); }
.st-cta p{ color:rgba(255,255,255,.75); max-width:620px; margin:24px auto 0; }
.st-cta .st-btns{ justify-content:center; }
.st-cta .btn{ color:var(--gold-light); }
.st-cta .btn::before{ background:var(--gold-light); }
.st-cta .btn:hover{ color:var(--black); }
.st-notes{ padding:48px 0 72px; }
.st-notes p{ font-size:12px; color:var(--ink-faint); max-width:900px; margin-top:8px; line-height:1.6; }
.why .why-mark.dash{ width:40px; height:1px; background:var(--gold-light); }
</style>"""

ST_JS = """<script>
document.querySelectorAll('.accordion').forEach(acc=>{
  acc.querySelectorAll('.acc-item').forEach(item=>{
    const btn=item.querySelector('.acc-btn'), panel=item.querySelector('.acc-panel');
    btn.addEventListener('click',()=>{
      const was=item.classList.contains('open');
      acc.querySelectorAll('.acc-item.open').forEach(o=>{ o.classList.remove('open'); o.querySelector('.acc-btn').setAttribute('aria-expanded','false'); o.querySelector('.acc-panel').style.maxHeight=0; });
      if(!was){ item.classList.add('open'); btn.setAttribute('aria-expanded','true'); panel.style.maxHeight=panel.scrollHeight+'px'; }
    });
  });
});
</script>"""

def stellest_schema(lang, t, pr):
    url = f"{DOMAIN}{PATH[lang]}stellest/"
    plain = lambda x: re.sub(r"<[^>]+>", "", x)
    prod = {"@context": "https://schema.org", "@type": "Product",
            "name": "Essilor Stellest", "brand": {"@type": "Brand", "name": "Essilor"},
            "description": plain(t["desc"]), "image": f"{DOMAIN}/img/og-stellest.jpg", "url": url,
            "offers": [{"@type": "Offer", "name": plain(name), "price": str(pr[k]["one_num"]), "priceCurrency": "RSD",
                        "availability": "https://schema.org/InStock", "url": url,
                        "seller": {"@type": "Optician", "name": "Optika Ginter", "url": DOMAIN + "/"}}
                       for k, name, _ in t["price_rows"]]}
    faq = {"@context": "https://schema.org", "@type": "FAQPage",
           "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t["faq"]]}
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": t["crumb_home"], "item": DOMAIN + PATH[lang]},
        {"@type": "ListItem", "position": 2, "name": "Stellest", "item": url}]}
    return "\n".join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + "</script>" for x in (prod, faq, crumbs))

def stellest_page(lang, d, v, root):
    t = ST[lang]; pr = st_prices(lang); img = root + "img/"
    tel = f"tel:{PHONE_TEL}"
    btns = (f'<div class="st-btns"><a href="{tel}" class="btn dark"><span>{t["btn_call"]} · {PHONE_DISPLAY}</span></a>'
            f'<a href="../okviri/" class="btn"><span>{t["btn_frames"]}</span></a></div>')
    li = lambda items: "".join(f"<li><b>{a}</b>{b}</li>" if isinstance(items[0], tuple) else f"<li>{a}</li>"
                               for a, b in (items if isinstance(items[0], tuple) else [(x, "") for x in items]))
    rows = "".join(f"""<div class="st-prow"><div><h3>{name}</h3><p>{sub}</p></div>
  <div><span class="st-pl">{t['price_base']}</span><span class="st-old">{pr[k]['base']} RSD</span> <span class="st-pair">{t['price_per']}</span></div>
  <div><span class="st-pl">{t['price_ours']} · −10%</span><span class="st-new">{pr[k]['one']} RSD</span><span class="st-pair">{t['price_per']} · {pr[k]['pair']} RSD {t['price_pair']}</span></div></div>"""
                   for k, name, sub in t["price_rows"])
    how = "".join(f'<div class="why-item"><span class="why-mark dash"></span><h3>{a}</h3><p>{b}</p></div>' for a, b in t["how"])
    tips = "".join(f'<div class="st-tip"><span class="why-mark"></span><h3>{a}</h3><p>{b}</p></div>' for a, b in t["tips"])
    faq = "\n".join(f'<div class="acc-item"><button class="acc-btn" aria-expanded="false"><h3 class="acc-title">{q}</h3><span class="acc-icon"></span></button><div class="acc-panel"><div class="acc-panel-in">{a}</div></div></div>' for q, a in t["faq"])
    body = f"""<section class="sub-top st-top"><div class="wrap st-hero">
  <div>
    <span class="kicker">{t['kicker']}</span>
    <h1 class="h-sec">{t['h1']}</h1>
    <span class="sub-rule"></span>
    <p class="lead">{t['lead']}</p>
    <span class="st-badge">{t['badge']}</span>
    {btns}
  </div>
  <div class="st-frame"><img src="{img}stellest-hero-1200.webp" srcset="{img}stellest-hero-800.webp 800w, {img}stellest-hero-1200.webp 1200w" sizes="(min-width:960px) 50vw, 100vw" width="1200" height="630" alt="{t['img_alt']}"></div>
</div></section>
<section class="st-panel"><div class="wrap st-text">
  <h2 class="h-sec">{t['why_h']}</h2>
  {''.join(f'<p>{p}</p>' for p in t['why_p'])}
</div></section>
<section class="why"><div class="wrap">
  <div class="sec-head"><span class="kicker">{t['how_kicker']}</span><h2 class="h-sec">{t['how_h']}</h2></div>
  <div class="why-grid" style="margin-top:48px">{how}</div>
</div></section>
<section><div class="wrap st-stat">
  <div class="st-frame"><img src="{img}stellest-boy-900.webp" srcset="{img}stellest-boy-600.webp 600w, {img}stellest-boy-900.webp 900w" sizes="(min-width:960px) 45vw, 100vw" width="900" height="900" alt="{t['img2_alt']}" loading="lazy"></div>
  <div>
    <div class="st-num">{t['stat_b']}</div><p class="st-num-t">{t['stat']}</p>
    <span class="kicker" style="margin-top:56px">{t['for_kicker']}</span>
    <h2 class="h-sec" style="font-size:clamp(30px,4vw,48px)">{t['for_h']}</h2>
    <ul class="st-list">{li(t['for_list'])}</ul>
  </div>
</div></section>
<section class="st-panel"><div class="wrap">
  <span class="kicker">{t['steps_kicker']}</span><h2 class="h-sec">{t['steps_h']}</h2>
  <ul class="st-list" style="max-width:900px">{li(t['steps'])}</ul>
  <div class="st-video st-frame"><video controls preload="none" playsinline poster="{img}stellest-poster.webp" width="1280" height="720" title="{t['video_title']}"><source src="{img}stellest-video.mp4" type="video/mp4"></video></div>
</div></section>
<section id="cena"><div class="wrap">
  <span class="kicker">{t['price_kicker']}</span><h2 class="h-sec">{t['price_h']}</h2>
  <div class="st-price">{rows}</div>
  <p class="st-note">{t['price_note']}</p>
  <span class="kicker" style="margin-top:72px">{t['guar_kicker']}</span><h2 class="h-sec" style="font-size:clamp(30px,4vw,48px)">{t['guar_h']}</h2>
  <p class="lead" style="max-width:760px">{t['guar_p']}</p>
</div></section>
<section class="st-panel"><div class="wrap">
  <span class="kicker">{t['tips_kicker']}</span><h2 class="h-sec">{t['tips_h']}</h2>
  <div class="st-tips">{tips}</div>
</div></section>
<section class="st-faq"><div class="wrap" style="max-width:1000px">
  <span class="kicker">{t['faq_kicker']}</span><h2 class="h-sec">{t['faq_h']}</h2>
  <div class="accordion">{faq}</div>
</div></section>
<section class="st-cta"><div class="wrap">
  <h2 class="h-sec">{t['cta_h']}</h2><p>{t['cta_p']}</p>
  <div class="st-btns"><a href="{tel}" class="btn"><span>{t['btn_call']} · {PHONE_DISPLAY}</span></a><a href="../okviri/" class="btn"><span>{t['btn_frames']}</span></a></div>
</div></section>
<div class="st-notes"><div class="wrap"><span class="kicker">{t['notes_h']}</span>{''.join(f'<p>{n}</p>' for n in t['notes'])}</div></div>
{stellest_schema(lang, t, pr)}"""
    v.update({"SUB_TITLE": t["title"], "SUB_DESC": t["desc"], "BODY": body,
              "SUB_SCRIPT": ST_JS, "OG_IMG": "og-stellest.jpg",
              "SUB_CSS_LINK": ST_CSS})

VX_FMT = {"sr": ("od {} RSD", "par od {} RSD"), "hu": ("{} RSD-tól", "pár {} RSD-tól"),
          "en": ("from {} RSD", "pair from {} RSD"), "ru": ("от {} RSD", "пара от {} RSD")}
VX_PER = {"sr": "po staklu", "hu": "lencsénként", "en": "per lens", "ru": "за линзу"}
VX_SLUG = "progresivne-naocare"

def vx_schema(lang, t, pr):
    url = f"{DOMAIN}{PATH[lang]}{VX_SLUG}/"
    plain = lambda x: re.sub(r"<[^>]+>", "", x)
    prods = [{"@context": "https://schema.org", "@type": "Product", "name": name,
              "brand": {"@type": "Brand", "name": "Varilux"}, "description": plain(txt), "url": url,
              "image": f"{DOMAIN}/img/og-varilux.jpg",
              "offers": {"@type": "Offer", "price": str(pr[k]["one_num"]), "priceCurrency": "RSD", "url": url,
                         "availability": "https://schema.org/InStock",
                         "seller": {"@type": "Optician", "name": "Optika Ginter", "url": DOMAIN + "/"}}}
             for k, name, _, txt in t["lines"]]
    faq = {"@context": "https://schema.org", "@type": "FAQPage",
           "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t["faq"]]}
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": t["crumb_home"], "item": DOMAIN + PATH[lang]},
        {"@type": "ListItem", "position": 2, "name": "Varilux", "item": url}]}
    return "\n".join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + "</script>" for x in prods + [faq, crumbs])

def vx_service(lang):
    t = VX[lang]
    return (t["svc_title"], t["svc_price"], f'{t["svc_text"]} <a class="link-gold" href="{VX_SLUG}/">{t["svc_more"]} →</a>')

def vx_page(lang, d, v, root):
    t = VX[lang]; pr = vx_prices(lang); img = root + "img/"; tel = f"tel:{PHONE_TEL}"
    f1, f2 = VX_FMT[lang]
    btns = (f'<div class="st-btns"><a href="{tel}" class="btn dark"><span>{t["btn_call"]} · {PHONE_DISPLAY}</span></a>'
            f'<a href="../okviri/" class="btn"><span>{t["btn_frames"]}</span></a></div>')
    li = lambda items: "".join(f"<li><b>{a}</b>{b}</li>" for a, b in items)
    rows = "".join(f"""<div class="st-prow{' vx-rec' if k in ('comfort','physio') else ''}"><div><span class="st-pl vx-tag">{tag}</span><h3>{name}</h3></div>
  <div><p class="vx-txt">{txt}</p></div>
  <div><span class="st-new">{f1.format(pr[k]['one'])}</span><span class="st-pair">{VX_PER[lang]} · {f2.format(pr[k]['pair'])}</span></div></div>"""
                   for k, name, tag, txt in t["lines"])
    zones = "".join(f'<div class="why-item"><span class="why-mark dash"></span><h3>{a}</h3><p>{b}</p></div>' for a, b in t["zones"])
    guar = "".join(f'<div class="st-tip"><span class="why-mark"></span><h3>{a}</h3><p>{b}</p></div>' for a, b in t["guar"])
    tips = "".join(f'<div class="st-tip"><span class="why-mark"></span><h3>{a}</h3><p>{b}</p></div>' for a, b in t["tips"])
    faq = "\n".join(f'<div class="acc-item"><button class="acc-btn" aria-expanded="false"><h3 class="acc-title">{q}</h3><span class="acc-icon"></span></button><div class="acc-panel"><div class="acc-panel-in">{a}</div></div></div>' for q, a in t["faq"])
    body = f"""<section class="sub-top st-top"><div class="wrap st-hero">
  <div>
    <span class="kicker">{t['kicker']}</span>
    <h1 class="h-sec">{t['h1']}</h1>
    <span class="sub-rule"></span>
    <p class="lead">{t['lead']}</p>
    <span class="st-badge">{t['badge']}</span>
    {btns}
  </div>
  <div class="st-frame"><img src="{img}varilux-hero-1200.webp" srcset="{img}varilux-hero-800.webp 800w, {img}varilux-hero-1200.webp 1200w" sizes="(min-width:960px) 50vw, 100vw" width="1200" height="630" alt="{t['img_alt']}"></div>
</div></section>
<section class="st-panel"><div class="wrap st-stat">
  <div class="st-text">
    <h2 class="h-sec">{t['what_h']}</h2>
    {''.join(f'<p>{p}</p>' for p in t['what_p'])}
  </div>
  <div class="st-frame"><img src="{img}varilux-reading-900.webp" srcset="{img}varilux-reading-600.webp 600w, {img}varilux-reading-900.webp 900w" sizes="(min-width:960px) 45vw, 100vw" width="900" height="900" alt="{t['img2_alt']}" loading="lazy"></div>
</div></section>
<section class="why"><div class="wrap">
  <div class="sec-head"><span class="kicker">{t['zones_kicker']}</span><h2 class="h-sec">{t['zones_h']}</h2></div>
  <div class="why-grid" style="margin-top:48px">{zones}</div>
</div></section>
<section id="cena"><div class="wrap">
  <span class="kicker">{t['lines_kicker']}</span><h2 class="h-sec">{t['lines_h']}</h2>
  <p class="lead" style="max-width:760px">{t['lines_lead']}</p>
  <div class="st-price">{rows}</div>
  <p class="st-note">{t['price_note']}</p>
</div></section>
<section class="st-panel"><div class="wrap">
  <span class="kicker">{t['steps_kicker']}</span><h2 class="h-sec">{t['steps_h']}</h2>
  <ul class="st-list" style="max-width:900px">{li(t['steps'])}</ul>
  <div class="st-video st-frame"><video controls preload="none" playsinline poster="{img}varilux-poster.webp" width="1280" height="720" title="{t['video_title']}"><source src="{img}varilux-video.mp4" type="video/mp4"></video></div>
</div></section>
<section><div class="wrap">
  <span class="kicker">{t['guar_kicker']}</span><h2 class="h-sec">{t['guar_h']}</h2>
  <div class="st-tips vx-3">{guar}</div>
</div></section>
<section class="st-panel"><div class="wrap">
  <span class="kicker">{t['tips_kicker']}</span><h2 class="h-sec">{t['tips_h']}</h2>
  <div class="st-tips">{tips}</div>
</div></section>
<section class="st-faq"><div class="wrap" style="max-width:1000px">
  <span class="kicker">{t['faq_kicker']}</span><h2 class="h-sec">{t['faq_h']}</h2>
  <div class="accordion">{faq}</div>
</div></section>
<section class="st-cta"><div class="wrap">
  <h2 class="h-sec">{t['cta_h']}</h2><p>{t['cta_p']}</p>
  <div class="st-btns"><a href="{tel}" class="btn"><span>{t['btn_call']} · {PHONE_DISPLAY}</span></a><a href="../okviri/" class="btn"><span>{t['btn_frames']}</span></a></div>
</div></section>
<div class="st-notes"><div class="wrap"><span class="kicker">{t['notes_h']}</span>{''.join(f'<p>{n}</p>' for n in t['notes'])}</div></div>
{vx_schema(lang, t, pr)}"""
    css = ST_CSS.replace("</style>", """.vx-tag{ color:var(--gold-deep); }
.vx-txt{ color:var(--ink-soft) !important; font-size:15px !important; margin-top:0 !important; }
.vx-rec h3{ color:var(--ink); }
.vx-rec{ border-left:2px solid var(--gold); padding-left:20px; }
@media(min-width:900px){ .st-prow{ grid-template-columns:1fr 1.4fr .9fr; } }
@media(min-width:1100px){ .st-tips.vx-3{ grid-template-columns:repeat(3,1fr); } }
</style>""")
    v.update({"SUB_TITLE": t["title"], "SUB_DESC": t["desc"], "BODY": body,
              "SUB_SCRIPT": ST_JS, "OG_IMG": "og-varilux.jpg", "SUB_CSS_LINK": css})

def build_sub(lang, slug):
    d, v = base_vars(lang)
    root = ROOT[lang] + "../"          # od /okviri/ ili /ru/okviri/ do korena sajta
    v.update({**asset_vars(root), "ROOT": root, "HOME": "../", "FRAMES_URL": "../okviri/" if slug != "okviri" else "./",
              "PRIVACY_URL": "../privatnost/" if slug != "privatnost" else "./",
              "STELLEST_URL": "../stellest/" if slug != "stellest" else "./",
              "VX_URL": "../progresivne-naocare/" if slug != "progresivne-naocare" else "./",
              "FRAMES_ACTIVE": ' class="active" aria-current="page"' if slug == "okviri" else "",
              "LANG_SWITCH": lang_switch(lang, root, slug)})
    if slug == "okviri":
        filt = lambda f, val, txt, on=False: f'<button type="button" class="chip" data-f="{f}" data-v="{val}" aria-pressed="{"true" if on else "false"}">{txt}</button>'
        body = f"""<section class="sub-top"><div class="wrap">
  <span class="kicker">{d['cat_kicker']}</span>
  <h1 class="h-sec">{d['cat_h']}</h1>
  <span class="sub-rule"></span>
  <div class="cat-intro"><p class="lead">{d['cat_lead']}</p>
  <p class="cat-note">{d['cat_note']}</p></div>
  <div class="cat-filters" role="group">
    <select class="chip is-on" id="fCat" aria-label="{d['f_kind_opt']}"><option value="opticki" selected>{d['f_kind_opt']}</option><option value="suncani">{d['f_kind_sun']}</option></select>
    <select class="chip" id="fGender" aria-label="{d['f_gender_all']}"><option value="">{d['f_gender_all']}</option><option value="zenski">{d['f_women']}</option><option value="muski">{d['f_men']}</option><option value="deciji">{d['f_kids']}</option><option value="uniseks">{d['f_unisex']}</option></select>
    <select class="chip" id="fBrand" aria-label="{d['f_brand_all']}"><option value="">{d['f_brand_all']}</option></select>
    <select class="chip" id="fPrice" aria-label="{d['f_price_all']}"><option value="">{d['f_price_all']}</option><option value="900-3900">900–3 900</option><option value="4000-9900">4 000–9 900</option><option value="10000-15000">10 000–15 000</option><option value="15000-">{d['f_p4']}</option></select>
    <select class="chip" id="fSort" aria-label="{d['f_sort_rec']}"><option value="">{d['f_sort_rec']}</option><option value="new">{d['f_sort_new']}</option><option value="asc">{d['f_sort_asc']}</option><option value="desc">{d['f_sort_desc']}</option></select>
    {filt('sale', '1', d['f_sale'])}
    <p class="cat-count" id="catCount"></p>
  </div>
</div></section>
<section class="cat-grid-sec"><div class="wrap"><div class="cat-grid" id="catGrid"></div>
  <div class="cat-intro-m"><p class="lead">{d['cat_lead']}</p><p class="cat-note">{d['cat_note']}</p></div></div></section>
<div class="fm" id="fm" role="dialog" aria-modal="true" aria-labelledby="fmTitle"><div class="fm-box">
  <button type="button" class="fm-close" id="fmClose" aria-label="{d['close']}">&times;</button>
  <div id="fmBody"></div>
</div></div>"""
        tkeys = [k for k in CAT[lang] if k.startswith(("cat_", "f_", "l_", "s_", "r_", "e_"))]
        cfg = {"lang": lang, "url": SUPA_URL, "key": SUPA_KEY, "fn": SUPA_URL + "/functions/v1/reserve-frame",
               "phone": PHONE_DISPLAY, "phoneTel": PHONE_TEL, "privacyUrl": "../privatnost/",
               "t": {k: CAT[lang][k] for k in tkeys}, "dict": VALUE_DICT}
        script = ("<script>window.CAT_CFG=" + json.dumps(cfg, ensure_ascii=False).replace("</", "<\\/") + ";</script>\n"
                  f'<script src="{root}assets/catalog.js?v={ASSET_V}"></script>')
        v.update({"SUB_TITLE": d["cat_title"], "SUB_DESC": d["cat_desc"], "BODY": body, "SUB_SCRIPT": script})
    elif slug == "stellest":
        stellest_page(lang, d, v, root)
    elif slug == "progresivne-naocare":
        vx_page(lang, d, v, root)
    else:
        pr = PRIV[lang]
        fmt = lambda t: t.format(ADDRESS=ADDRESS, CITY=CITY, PIB=PIB, MB=MB, EMAIL=EMAIL,
                                  PHONE=f'<a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>')
        secs = "\n".join(f'    <div class="priv-sec"><h2>{h}</h2><p>{fmt(t)}</p></div>' for h, t in pr["priv_sections"])
        body = f"""<section class="sub-top"><div class="wrap">
  <span class="kicker">{pr['priv_kicker']}</span>
  <h1 class="h-sec">{pr['priv_h']}</h1>
  <span class="sub-rule"></span>
</div></section>
<section class="priv"><div class="wrap"><div class="priv-in">
{secs}
  <p class="priv-upd">{pr['priv_updated']}</p>
</div></div></section>"""
        v.update({"SUB_TITLE": pr["priv_title"], "SUB_DESC": pr["priv_desc"], "BODY": body, "SUB_SCRIPT": ""})
    v["SUB_SEO"] = sub_seo(lang, slug, v["SUB_TITLE"], v["SUB_DESC"], v.pop("OG_IMG", "og-image.jpg"))
    v.setdefault("FRAMES_ACTIVE", "")
    return render(SUB_TPL, v)

os.makedirs(OUT + "/assets", exist_ok=True)
open(OUT + "/assets/site.css", "w", encoding="utf-8").write(SITE_CSS + "\n")
open(OUT + "/assets/logos.svg", "w", encoding="utf-8").write(SPRITE)
open(OUT + "/assets/favicon.svg", "w", encoding="utf-8").write(fav)
open(OUT + "/assets/catalog.css", "w", encoding="utf-8").write(CAT_CSS)
open(OUT + "/assets/catalog.js", "w", encoding="utf-8").write(CAT_JS)
for l in LANGS:
    p = OUT + PATH[l]; os.makedirs(p, exist_ok=True)
    open(p + "index.html", "w", encoding="utf-8").write(build(l))
    for slug in SUB_PAGES:
        os.makedirs(p + slug, exist_ok=True)
        open(p + slug + "/index.html", "w", encoding="utf-8").write(build_sub(l, slug))
urls = "\n".join(f"  <url><loc>{DOMAIN}{PATH[l]}{s}</loc>" + "".join(f'<xhtml:link rel="alternate" hreflang="{a}" href="{DOMAIN}{PATH[a]}{s}"/>' for a in LANGS) + "</url>" for s in ["", "okviri/", "progresivne-naocare/", "stellest/", "privatnost/"] for l in LANGS)
open(OUT + "/sitemap.xml", "w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n{urls}\n</urlset>\n')
open(OUT + "/robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
print("ok")
