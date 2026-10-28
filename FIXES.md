# FIXES.md — Optika Ginter (sajt)

## 2026-10-28 — Katalog okvira i politika privatnosti
- Новые страницы на 4 языках: `/okviri/` (каталог оправ) и `/privatnost/` (политика конфиденциальности); ссылки в меню и футере, sitemap обновлён
- Каталог читает опубликованные оправы из Ginter CRM (Supabase, таблица `frames`, только публичные поля). Фильтры: optički / sunčani, ženski / muški / dečiji, akcija, brend. Карточка оправы: фото, цена (со скидкой), описание на языке страницы, параметры, форма «Rezervišite» (ime, prezime, telefon, согласие) → Edge Function `reserve-frame` → бронь в CRM + Telegram Анне
- Общие файлы вынесены в `assets/` (site.css, catalog.css, catalog.js, favicon.svg, logos.svg — спрайт логотипов), страницы стали ~28 KB вместо ~350 KB
- Исходники: `_izvor/build.py` (сборка), `_izvor/sub.html`, `_izvor/catalog_content.py` (тексты каталога и политики), `_izvor/catalog.css`, `_izvor/catalog.js`
- Публикация: main → gh-pages (fast-forward)
