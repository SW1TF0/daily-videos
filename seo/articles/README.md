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
