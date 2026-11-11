# SEO дневник

Най-новото е най-отгоре.

## Следващи стъпки (по приоритет)
1. ✅ Search Console свързан, sitemap изпратен (11.11). По желание собственикът: „Проверка на URL“ → „Заявка за индексиране“ за `/bg/`, `/tr/` и новите страници за услуги (няма API за това). Аз меря с `inspect-sitemap` на 2–3 дни.
2. **Собственикът:** Google Business Profile „SmartMenuKJ“ (ул. Джебелска 2, Кърджали): категории, 6-те услуги, телефон, линк към `/bg/`, снимки. Най-силният сигнал за „… Кърджали“ в картите.
3. Страниците за услугите: текстовете (BG) са в `seo/pages/` (M-1111-09) → програмистът ги прави на страници; после EN/TR версии и проверка на живо със `site_shot.js`.
4. JSON-LD: FAQPage за FAQ на началната; `openingHours` и `geo` (само ако собственикът даде часове/координати); Service URL-ите в BG/TR версиите да сочат към `/bg/…`, `/tr/…`.
5. H1 на началната (`Технологии, на които бизнесът ви може да разчита.`) без услуга и град → да съдържа „Кърджали“ (напр. подзаглавие/h1 „Сайтове, камери, умен дом и QR менюта в Кърджали“).
6. Още текст: about (172 думи) и portfolio (207 думи) са тънки; services ~80 думи на услуга. Факти от собственика за проекти в портфолиото.
7. Линкове: Instagram/TikTok/YouTube био → `https://www.smartmenukj.com/bg/` (през мениджъра към Плочко); местни каталози (собственикът).

## 11.11.2026 — M-1111-22 — sitemap изпратен пак 12:28 UTC; Google вече го прочете: 43 адреса, 0 грешки. Готово ✅ в групата (15/43, причини: нови страници още не обходени; 10 непознати до днешния sitemap; слаби вътрешни линкове).

## 11.11.2026 — Search Console свързан (service account, свойство https://www.smartmenukj.com/, siteOwner)
- Хостове oauth2/searchconsole/www.googleapis.com добавени в средата (одобрено).
- ✅ sitemap.xml изпратен 12:18 UTC; 0 грешки. GSC още помни старото четене (21 URL, pending) — живият sitemap има 43 URL.
- inspect-sitemap: **15 от 43 индексирани** (EN начална, services EN/BG, about ×3, privacy ×3, terms EN/BG, contact BG/TR, portfolio TR, blog/qr-menu-kak-raboti).
- Не индексирани: 19 „открита – не е индексирана“ (повечето нови страници за услуги, tr/terms, 2 статии), 10 „не е известен на Google“ (cctv, umen-dom BG, компютърен сервис ×3, bg/blog/ …). Сред неиндексираните са и /bg/ и /tr/ началните.
- Следва: повторен inspect-sitemap след 2–3 дни; вътрешни линкове от началната/services към новите страници; GBP от собственика.

## 11.11.2026 — M-1111-18 — пускане на /bg/blog/
❌ add_repo SW1TF0/SmartMenu (push) отказан пак: „denied by the Claude Code auto mode classifier. Reason: [Access Added As A Means]“. Предадено на мениджъра → програмиста (текстове в seo/articles/, генератор по модела на tools/build-service-pages.mjs). За собственика: permission rule за mcp__claude-code-remote__add_repo в сесията на SEO.

## 11.11.2026 — M-1111-16 — 3 статии за блога (BG)
✅ `seo/articles/`: qr-menu-kak-raboti (647 думи), videonablyudenie-predi-montazh (691), umen-dom-ot-kade-da-zapochnete (646). Title ≤60 и description ≤155 знака с Кърджали, 5 FAQ, линкове към живите страници на услугите (проверени, 200). README е бележка за програмиста: /bg/blog/, BlogPosting + FAQPage + Breadcrumb, sitemap, линкове от услугите. Само факти от сайта; общите съвети са без числа и обещания.
Сам не съм ги пуснал: имам само четене на SmartMenu (add_repo push беше отказан).

## 11.11.2026 — M-1111-14 — текстове за Google Business Profile
✅ `seo/gbp.md`: стъпки за създаване и потвърждение, описание (656 зн.), главна + 8 допълнителни категории, зони на обслужване, 6 услуги с линкове към новите страници, атрибути и данни, 5 първи поста, 10 въпроса и отговора. Само факти от сайта; работно време, снимки и реалните населени места оставих като [попълни] за собственика.
Остава: собственикът създава профила; после линкът отива в sameAs на сайта.

## 11.11.2026 — M-1111-12 — EN и TR версии на 6-те страници
✅ `seo/pages/en/` (qr-menu, web-design, cctv, smart-home, 3d-printing, computer-repair) и `seo/pages/tr/` (qr-menu, web-sitesi, guvenlik-kamerasi, akilli-ev, 3d-baski, bilgisayar-servisi). Текстът е естествен, не дословен; взимах думите от EN/TR версиите на services/index на сайта. Kardzhali / Kırcaali (както е на сайта). Title ≤60, description ≤155, H1, 4 FAQ, вътрешни линкове в езика. EN е в корена (/…), защото сайтът няма /en/. README: таблица bg↔en↔tr за hreflang. keywords.md: думи на 3 езика (12 EN, 14 TR).
Остава: програмистът → страници; проверка на живо.

## 11.11.2026 — M-1111-09 — текстове за 6 страници на услугите (BG)
✅ `seo/pages/`: qr-menu, saitove, videonablyudenie, umen-dom, 3d-pechat, kompyutaren-servis (+ README с указания за програмиста: шаблон, canonical, FAQPage/Service/Breadcrumb JSON-LD, sitemap, линкове от services и началната). По 350–415 думи, title ≤60 и description ≤155 знака с „Кърджали“, H1, 4–5 FAQ, вътрешни линкове между страниците. Факти само от BG services/index/about/contact (вкл. текстовете „За дома“) и playbook.md; без цени и нови клиенти (примерите са само проектите, които вече са на сайта).
Остава: програмистът → страници; EN/TR; проверка на живо.

## 11.11.2026 — първи одит на smartmenukj.com (само преглед, без промени)
Проверено: repo `SW1TF0/smartmenu` (commit d49a077), живия сайт с `site_shot.js` (телефон + компютър: `/bg/`, `/bg/services.html`, `/bg/contact.html`, `/bg/portfolio.html`, `/bg/about.html`, `/tr/`), curl на пренасочванията. Sitemap/robots ги оправя програмистът (M-1111-07) — не съм ги пипал.

**Хостинг:** GitHub Pages (`CNAME` www.smartmenukj.com; `firebase.json` е за Firestore/запасен — `cleanUrls` там не важи на живо).

### Добре ✅
- `smartmenukj.com` → 301 → `www.`; `/bg` → 301 → `/bg/`; 404 връща истински 404.
- 3 езика (EN `/`, BG `/bg/`, TR `/tr/`), `lang` верен, hreflang + x-default (bg) на всяка страница и в sitemap.
- Canonical на всяка страница, уникални title/description с „Кърджали“ в BG/TR, по 1 h1, alt на всички снимки.
- robots.txt: Allow /, Disallow admin/account/login, линк към sitemap. sitemap.xml: 21 URL (7 страници × 3 езика).
- Езиковото пренасочване по браузъра изключва ботовете (Googlebot вижда всяка версия).
- JSON-LD LocalBusiness (адрес ул. Джебелска 2, 6600, телефон, areaServed, sameAs Instagram, каталог с 6-те услуги).
- Без конзолни грешки и счупени линкове; снимките са малки (WebP 400×400, папка img/ 360K).
- Шрифтовете са локални (без Google Fonts).

### Пречи ❌ (по тежест)
1. **Няма страница за отделна услуга.** И 6-те услуги са секции (`#menu`, `#web`, `#cameras`…) в една `services.html` с ~500 думи общо (~80 на услуга). Google класира страници, не секции → за „видеонаблюдение Кърджали“ или „QR меню Кърджали“ няма силна целева страница.
2. **Не знаем дали сме индексирани.** Няма данни от Search Console; `site:` не мога да проверя оттук. Има файл за потвърждение `googleb16e88fb77a3c435.html` → Search Console вероятно е заявен, но не знам дали sitemap е изпратен.
3. **Google Business Profile** — не знам дали го има/попълнен е; за местни търсения това е №1.
4. **H1 на началната е общ** („Технологии, на които бизнесът ви може да разчита.“) — без услуга и град.
5. **Тънки страници:** about 172 думи, portfolio 207 думи; „Кърджали“ само 4 пъти в BG services.
6. **JSON-LD непълен:** няма FAQPage (а FAQ секция има), openingHours, geo; Service URL-ите са само към EN `services.html#…`.
7. `/bg/services` и `/bg/services.html` дават 200 и двете (дубликат) — canonical го покрива, достатъчно е.
8. Корен: `Screenshot 2026-10-13 at 20.47.37.png` и PNG-та в корена са публични — не пречат, но може да се почистят (програмистът).

Бележка: на контакта `contact.js` не се зарежда тук, защото средата блокира www.gstatic.com (Firebase) — не е грешка на сайта.
