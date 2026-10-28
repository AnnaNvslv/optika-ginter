# Сборка сайта: python3 build.py  -> папка OUT (4 языка + img + sitemap)
import json, os, re, shutil, urllib.parse, html as H
from content import *
from catalog_content import CAT, PRIV, VALUE_DICT

DOMAIN = "https://optikaginter.rs"
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(BASE)  # корень репозитория
IMG_V = "9"  # менять при замене фото, чтобы браузер не брал старые
ASSET_V = "4"  # менять при изменении base.css или логотипов (папка assets/)
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
SUB_PAGES = ["okviri", "privatnost"]
fav = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{P["logo-og"]["vb"]}"><path d="{P["logo-og"]["d"]}"/></svg>'
# Zajednički fajlovi (assets/): stil, logotipi i favicon se učitavaju jednom i keširaju,
# umesto da se ugrađuju u svaku stranicu.
SPRITE = '<svg xmlns="http://www.w3.org/2000/svg">' + "".join(
    f'<symbol id="{sid}" viewBox="{P[n]["vb"]}"><path d="{P[n]["d"]}"/></symbol>'
    for sid, n in [("lg-full", "logo-full"), ("lg-og", "logo-og"), ("lg-hz", "logo-horizontal")]) + "</svg>"
SITE_CSS = re.sub(r"^\s*<style>\s*|\s*</style>\s*$", "", STYLE)

def services(d):
    out = []
    for i, (t, price, txt) in enumerate(d["services"]):
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

def build(lang):
    d, v = base_vars(lang); root = ROOT[lang]
    v.update({
        **asset_vars(root), "ROOT": root, "HOME": root or "./", "FRAMES_URL": "okviri/", "PRIVACY_URL": "privatnost/",
        "HEAD_SEO": head_seo(lang, d), "SCHEMA": schema(lang, d), "FAQ_SCHEMA": faq_schema(d),
        "LANG_SWITCH": lang_switch(lang, root),
        "SERVICES": services(d), "FAQ": faq(d), "WHY": why(d), "TEAM": team(d, root, ALT[lang][1]),
        "FRAMES": "".join(f'<span class="brand-tile">{b}</span>' for b in FRAMES), "LENSES": "".join(f'<span class="brand-tile">{b}</span>' for b in LENSES),
        "alt_salon": ALT[lang][0], "H1": d["title"].split(" | ")[0],
    })
    return render(TPL, v)

def sub_seo(lang, slug, title, desc):
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
<meta property="og:image" content="{DOMAIN}/img/og-image.jpg">
<meta property="og:locale" content="{LOCALE[lang]}">
<meta name="theme-color" content="#12100D">"""

def build_sub(lang, slug):
    d, v = base_vars(lang)
    root = ROOT[lang] + "../"          # od /okviri/ ili /ru/okviri/ do korena sajta
    v.update({**asset_vars(root), "ROOT": root, "HOME": "../", "FRAMES_URL": "../okviri/" if slug != "okviri" else "./",
              "PRIVACY_URL": "../privatnost/" if slug != "privatnost" else "./",
              "FRAMES_ACTIVE": ' class="active" aria-current="page"' if slug == "okviri" else "",
              "LANG_SWITCH": lang_switch(lang, root, slug)})
    if slug == "okviri":
        filt = lambda f, val, txt, on=False: f'<button type="button" class="chip" data-f="{f}" data-v="{val}" aria-pressed="{"true" if on else "false"}">{txt}</button>'
        body = f"""<section class="sub-top"><div class="wrap">
  <span class="kicker">{d['cat_kicker']}</span>
  <h1 class="h-sec">{d['cat_h']}</h1>
  <span class="sub-rule"></span>
  <p class="lead">{d['cat_lead']}</p>
  <div class="cat-filters" role="group">
    {filt('cat', '', d['f_all'], True)}{filt('cat', 'opticki', d['f_optical'])}{filt('cat', 'suncani', d['f_sun'])}
    <span class="cat-sep"></span>
    {filt('gender', 'zenski', d['f_women'])}{filt('gender', 'muski', d['f_men'])}{filt('gender', 'deciji', d['f_kids'])}
    {filt('sale', '1', d['f_sale'])}
    <select class="chip" id="fBrand" aria-label="{d['f_brand_all']}"><option value="">{d['f_brand_all']}</option></select>
  </div>
  <p class="cat-count" id="catCount"></p>
</div></section>
<section class="cat-grid-sec"><div class="wrap"><div class="cat-grid" id="catGrid"></div></div></section>
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
    v["SUB_SEO"] = sub_seo(lang, slug, v["SUB_TITLE"], v["SUB_DESC"])
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
urls = "\n".join(f"  <url><loc>{DOMAIN}{PATH[l]}{s}</loc>" + "".join(f'<xhtml:link rel="alternate" hreflang="{a}" href="{DOMAIN}{PATH[a]}{s}"/>' for a in LANGS) + "</url>" for s in ["", "okviri/", "privatnost/"] for l in LANGS)
open(OUT + "/sitemap.xml", "w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n{urls}\n</urlset>\n')
open(OUT + "/robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
print("ok")
