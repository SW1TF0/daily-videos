# Блог статии (M-1111-16) — бележка за програмиста

Три статии (BG), само с факти от smartmenukj.com. Всеки файл: URL, title (≤60), description (≤155), H1, дата, текст, FAQ, линкове към страниците на услугите.

## Как да станат раздел „Блог“ (/bg/blog/)
- Папка `bg/blog/`: `index.html` (списък: заглавие, дата, 1–2 изречения, линк) + по една страница на статия, в шаблона на страниците за услугите (хедър, футър, breadcrumb Начало › Блог › <статия>).
- Всяка статия: `<title>`, `<meta name="description">`, `<h1>` от файла; canonical към собствения URL; hreflang само `bg` + `x-default` (EN/TR още няма — не слагай alternate към несъществуващи страници).
- JSON-LD: `BlogPosting` (headline, datePublished, dateModified, author/publisher = `https://www.smartmenukj.com/#business`, mainEntityOfPage) + `FAQPage` за въпросите + `BreadcrumbList`.
- Линк „Блог“ във футъра (BG) и от всяка страница на услуга към свързаната статия („Прочетете още: …“).
- sitemap.xml: `/bg/blog/` + 3-те статии (lastmod = датата на публикуване).
- Без снимки от стокови сайтове; ако има реални снимки от обекти — с alt.

| Статия | Файл | URL | Свързана услуга |
|---|---|---|---|
| QR меню: как работи и какво печели заведението | qr-menu-kak-raboti.md | /bg/blog/qr-menu-kak-raboti.html | /bg/qr-menu-kardzhali.html |
| Видеонаблюдение за дом и бизнес: какво да знаете преди монтаж | videonablyudenie-predi-montazh.md | /bg/blog/videonablyudenie-predi-montazh.html | /bg/videonablyudenie-kardzhali.html |
| Умен дом: от какво да започнете | umen-dom-ot-kade-da-zapochnete.md | /bg/blog/umen-dom-ot-kade-da-zapochnete.html | /bg/umen-dom-kardzhali.html |
| Сайт за заведение или малък бизнес: какво трябва да има (M-1111-30) | sait-za-zavedenie-kakvo-tryabva-da-ima.md | /bg/blog/sait-za-zavedenie-kakvo-tryabva-da-ima.html | /bg/izrabotka-na-saitove-kardzhali.html |
| 3D печат: какво може да се направи и кога си струва (M-1111-30) | 3d-pechat-kakvo-moje-da-se-napravi.md | /bg/blog/3d-pechat-kakvo-moje-da-se-napravi.html | /bg/3d-pechat-kardzhali.html |
| Бавен компютър: 7 причини и кога да го дадете на сервиз (M-1111-30) | baven-kompyutar-7-prichini.md | /bg/blog/baven-kompyutar-7-prichini.html | /bg/kompyutaren-servis-kardzhali.html |

## M-1111-30 — качване на 3-те нови статии (за програмиста)
Същият шаблон и JSON-LD като първите 3 (BlogPosting + FAQPage + BreadcrumbList), sitemap + `/bg/blog/` списъка. Линковете в текста вече са в .md файловете. **Допълнителни линкове, за да има всяка статия ≥5 входящи** (блог списък + страница на услугата + 2 нови статии + 1 стара):
- Страница на услугата → „Прочетете още: <заглавие>“: `/bg/izrabotka-na-saitove-kardzhali.html` → сайт статията; `/bg/3d-pechat-kardzhali.html` → 3D статията; `/bg/kompyutaren-servis-kardzhali.html` → бавен компютър.
- В старите статии, в абзаца с линковете накрая:
  - `qr-menu-kak-raboti` → „Вижте и [какво трябва да има сайтът на заведението](/bg/blog/sait-za-zavedenie-kakvo-tryabva-da-ima.html).“
  - `videonablyudenie-predi-montazh` → „За офиса вижте и [Бавен компютър: 7 причини и кога да го дадете на сервиз](/bg/blog/baven-kompyutar-7-prichini.html).“
  - `umen-dom-ot-kade-da-zapochnete` → „Кутии и държачи по мярка: [какво може да се направи с 3D печат](/bg/blog/3d-pechat-kakvo-moje-da-se-napravi.html).“
- Новите статии вече линкват към старите (сайт → QR и камери; 3D → умен дом; компютър → камери) → старите стават с 3 → 4–5 входящи.

## M-1111-33 — EN и TR версии (seo/articles/en/, seo/articles/tr/)
Естествен текст на езика (не дословен превод), само факти от EN/TR страниците на услугите. Градът е изписан като на сайта: **Kardzhali** (EN) и **Kırcaali** (TR). Всеки файл има във frontmatter `lang` и адресите на другите два езика (`bg`/`en`/`tr`) — оттам идват hreflang тагове.

### hreflang: bg ↔ en ↔ tr
| BG (x-default) | EN | TR |
|---|---|---|
| /bg/blog/ | /blog/ | /tr/blog/ |
| /bg/blog/qr-menu-kak-raboti.html | /blog/qr-menu-how-it-works.html | /tr/blog/qr-menu-nasil-calisir.html |
| /bg/blog/videonablyudenie-predi-montazh.html | /blog/cctv-before-installation.html | /tr/blog/guvenlik-kamerasi-kurulum-oncesi.html |
| /bg/blog/umen-dom-ot-kade-da-zapochnete.html | /blog/smart-home-where-to-start.html | /tr/blog/akilli-ev-nereden-baslamali.html |
| /bg/blog/sait-za-zavedenie-kakvo-tryabva-da-ima.html | /blog/small-business-website-checklist.html | /tr/blog/isletme-web-sitesi-neler-olmali.html |
| /bg/blog/3d-pechat-kakvo-moje-da-se-napravi.html | /blog/3d-printing-what-can-be-made.html | /tr/blog/3d-baski-neler-yapilabilir.html |
| /bg/blog/baven-kompyutar-7-prichini.html | /blog/slow-computer-7-causes.html | /tr/blog/yavas-bilgisayar-7-neden.html |

За програмиста:
- Страниците `/blog/` и `/tr/blog/` (списък), статиите в шаблона на BG статиите (BlogPosting + FAQPage + BreadcrumbList; `inLanguage` en/tr), canonical към собствения адрес.
- **hreflang на всяка от 21-те страници (вкл. BG)**: `bg`, `en`, `tr` + `x-default` → BG, по таблицата; също в sitemap.xml (`xhtml:link`). На BG статиите днес е само `bg` + `x-default` — да се добавят `en` и `tr`.
- Футърът (`js/chrome.js` `blogLink()`): линк „Blog“/„Blog“ и на EN и TR страниците (сега само BG). Breadcrumb: Home › Blog / Ana sayfa › Blog.
- „Read more“ / „Devamını okuyun“ от всяка EN/TR страница на услуга към свързаната статия — същото съответствие като в BG (`service:` във frontmatter).
- sitemap: +14 адреса (2 списъка + 12 статии), после SEO агентът праща sitemaps-submit.
