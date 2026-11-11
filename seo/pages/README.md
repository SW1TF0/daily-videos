# Страници за услугите (M-1111-09) — текстове за програмиста

Шест целеви страници за местните търсения на 3 езика: BG тук, EN в `en/` (M-1111-12), TR в `tr/` (M-1111-12). Всеки файл има: URL, title, description, H1, текст, FAQ, вътрешни линкове.
Всички факти са от smartmenukj.com (services, index, about, contact — BG версиите, вкл. текстовете „За дома“) и `playbook.md`. Без цени, срокове извън „оферта до 24 ч.“, клиенти и отзиви.

## Как да се направят на страници (за програмиста)
- Шаблон: като `bg/services.html` (хедър, футър, Дом/Бизнес превключвател, бутон „Поискай оферта“ → `/bg/contact.html`).
- `<title>`, `<meta name="description">`, `<h1>` — точно от файла. canonical = собствения URL; hreflang bg (+ en/tr, когато ги има; дотогава само bg и x-default = bg).
- FAQ → видими `<details>` + JSON-LD `FAQPage` със същите въпроси/отговори. Плюс `Service` (provider = `https://www.smartmenukj.com/#business`, areaServed Кърджали) и `BreadcrumbList` (Начало › Услуги › <услуга>).
- Breadcrumb: Начало (`/bg/`) › Услуги (`/bg/services.html`) › <услугата>.
- Добави 6-те URL в `sitemap.xml`; в `bg/services.html` всяка секция да има линк „Научете повече →“ към своята страница; началната страница (картите с услугите) също да сочи към тях.
- Секциите „За дома“ (`data-for="personal"`) са по желание — текстът тук е общ и работи и за двете версии.

| Услуга | BG | EN (коренът на сайта е EN) | TR |
|---|---|---|---|
| QR меню | qr-menu.md → /bg/qr-menu-kardzhali.html | en/qr-menu.md → /qr-menu-kardzhali.html | tr/qr-menu.md → /tr/qr-menu-kircaali.html |
| Сайтове | saitove.md → /bg/izrabotka-na-saitove-kardzhali.html | en/web-design.md → /web-design-kardzhali.html | tr/web-sitesi.md → /tr/web-sitesi-kircaali.html |
| Видеонаблюдение | videonablyudenie.md → /bg/videonablyudenie-kardzhali.html | en/cctv.md → /cctv-kardzhali.html | tr/guvenlik-kamerasi.md → /tr/guvenlik-kamerasi-kircaali.html |
| Умен дом | umen-dom.md → /bg/umen-dom-kardzhali.html | en/smart-home.md → /smart-home-kardzhali.html | tr/akilli-ev.md → /tr/akilli-ev-kircaali.html |
| 3D печат | 3d-pechat.md → /bg/3d-pechat-kardzhali.html | en/3d-printing.md → /3d-printing-kardzhali.html | tr/3d-baski.md → /tr/3d-baski-kircaali.html |
| Компютърен сервиз | kompyutaren-servis.md → /bg/kompyutaren-servis-kardzhali.html | en/computer-repair.md → /computer-repair-kardzhali.html | tr/bilgisayar-servisi.md → /tr/bilgisayar-servisi-kircaali.html |

hreflang: всяка от трите версии сочи към другите две по реда в таблицата (bg, en, tr) + x-default = BG. Адресите (slug) са на езика на страницата, затова hreflang се взима от таблицата, а не от името на файла. EN файловете имат ред `hreflang:` с адресите.
