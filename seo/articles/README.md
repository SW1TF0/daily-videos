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
