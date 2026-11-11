# Страници за услугите (M-1111-09) — текстове за програмиста

Шест целеви страници за местните търсения (първо BG; EN/TR след това). Всеки файл има: URL, title, description, H1, текст, FAQ, вътрешни линкове.
Всички факти са от smartmenukj.com (services, index, about, contact — BG версиите, вкл. текстовете „За дома“) и `playbook.md`. Без цени, срокове извън „оферта до 24 ч.“, клиенти и отзиви.

## Как да се направят на страници (за програмиста)
- Шаблон: като `bg/services.html` (хедър, футър, Дом/Бизнес превключвател, бутон „Поискай оферта“ → `/bg/contact.html`).
- `<title>`, `<meta name="description">`, `<h1>` — точно от файла. canonical = собствения URL; hreflang bg (+ en/tr, когато ги има; дотогава само bg и x-default = bg).
- FAQ → видими `<details>` + JSON-LD `FAQPage` със същите въпроси/отговори. Плюс `Service` (provider = `https://www.smartmenukj.com/#business`, areaServed Кърджали) и `BreadcrumbList` (Начало › Услуги › <услуга>).
- Breadcrumb: Начало (`/bg/`) › Услуги (`/bg/services.html`) › <услугата>.
- Добави 6-те URL в `sitemap.xml`; в `bg/services.html` всяка секция да има линк „Научете повече →“ към своята страница; началната страница (картите с услугите) също да сочи към тях.
- Секциите „За дома“ (`data-for="personal"`) са по желание — текстът тук е общ и работи и за двете версии.

| Услуга | Файл | URL |
|---|---|---|
| QR меню | qr-menu.md | /bg/qr-menu-kardzhali.html |
| Сайтове | saitove.md | /bg/izrabotka-na-saitove-kardzhali.html |
| Видеонаблюдение | videonablyudenie.md | /bg/videonablyudenie-kardzhali.html |
| Умен дом | umen-dom.md | /bg/umen-dom-kardzhali.html |
| 3D печат | 3d-pechat.md | /bg/3d-pechat-kardzhali.html |
| Компютърен сервиз | kompyutaren-servis.md | /bg/kompyutaren-servis-kardzhali.html |
