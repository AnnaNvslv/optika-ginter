# Сборка сайта: python3 build.py  -> папка OUT (4 языка + img + sitemap)
import json, os, re, shutil, urllib.parse, html as H
from content import *

DOMAIN = "https://optikaginter.rs"
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(BASE)  # корень репозитория
IMG_V = "9"  # менять при замене фото, чтобы браузер не брал старые
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
fav = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{P["logo-og"]["vb"]}"><path d="{P["logo-og"]["d"]}"/></svg>'

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

def build(lang):
    d = dict(C[lang]); root = ROOT[lang]
    sw = "".join(f'<a href="{(root + PATH[l].lstrip("/")) or "./"}" hreflang="{l}" lang="{l}"' + (' class="active" aria-current="page"' if l == lang else "") + f">{l.upper()}</a>" for l in LANGS)
    v = {
        **{k: x for k, x in d.items() if isinstance(x, str)},
        "lang": lang, "ROOT": root, "HOME": root or "./", "STYLE": STYLE,
        "HEAD_SEO": head_seo(lang, d), "SCHEMA": schema(lang, d), "FAQ_SCHEMA": faq_schema(d),
        "FAVICON": "data:image/svg+xml," + urllib.parse.quote(fav),
        "LANG_SWITCH": f'<nav class="lang" aria-label="Language">{sw}</nav>',
        "SERVICES": services(d), "FAQ": faq(d), "WHY": why(d), "TEAM": team(d, root, ALT[lang][1]),
        "FRAMES": "".join(f'<span class="brand-tile">{b}</span>' for b in FRAMES), "LENSES": "".join(f'<span class="brand-tile">{b}</span>' for b in LENSES),
        "alt_salon": ALT[lang][0], "H1": d["title"].split(" | ")[0],
        "PHONE_DISPLAY": PHONE_DISPLAY, "PHONE_TEL": PHONE_TEL, "EMAIL": EMAIL, "INSTAGRAM": INSTAGRAM,
        "INSTAGRAM_HANDLE": INSTAGRAM_HANDLE, "ADDRESS": ADDRESS, "CITY": CITY, "PIB": PIB, "MB": MB,
    }
    for k, n in {"FULL": "logo-full", "OG": "logo-og", "HZ": "logo-horizontal"}.items():
        v["VB_" + k] = P[n]["vb"]; v["D_" + k] = P[n]["d"]; v["AR_" + k] = ar(P[n]["vb"])
    out = TPL
    for _ in range(2):
        out = re.sub(r"\{\{(\w+)\}\}", lambda m: v.get(m.group(1), m.group(0)), out)
    out = re.sub(r"(img/[\w-]+\.(?:webp|jpg))", r"\1?v=" + IMG_V, out)
    missing = set(re.findall(r"\{\{(\w+)\}\}", out))
    assert not missing, missing
    return out

for l in LANGS:
    p = OUT + PATH[l]; os.makedirs(p, exist_ok=True)
    open(p + "index.html", "w", encoding="utf-8").write(build(l))
urls = "\n".join(f"  <url><loc>{DOMAIN}{PATH[l]}</loc>" + "".join(f'<xhtml:link rel="alternate" hreflang="{a}" href="{DOMAIN}{PATH[a]}"/>' for a in LANGS) + "</url>" for l in LANGS)
open(OUT + "/sitemap.xml", "w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n{urls}\n</urlset>\n')
open(OUT + "/robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
print("ok")
