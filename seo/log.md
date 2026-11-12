# SEO дневник

Най-новото е най-отгоре.

## Следващи стъпки (по приоритет)
1. ✅ Search Console свързан, sitemap изпратен (11.11). По желание собственикът: „Проверка на URL“ → „Заявка за индексиране“ за `/bg/`, `/tr/` и новите страници за услуги (няма API за това). Аз меря с `inspect-sitemap` на 2–3 дни.
2. **Собственикът:** Google Business Profile „SmartMenuKJ“ (ул. Джебелска 2, Кърджали): категории, 6-те услуги, телефон, линк към `/bg/`, снимки. Най-силният сигнал за „… Кърджали“ в картите.
3. Страниците за услугите: текстовете (BG) са в `seo/pages/` (M-1111-09) → програмистът ги прави на страници; после EN/TR версии и проверка на живо със `site_shot.js`.
4. JSON-LD: FAQPage за FAQ на началната; `openingHours` и `geo` (само ако собственикът даде часове/координати); Service URL-ите в BG/TR версиите да сочат към `/bg/…`, `/tr/…`.
5. ✅ H1 на началната вече е с услуги + Кърджали на EN/BG/TR (проверено 12.11).
8. ✅ (12.11, на живо) `/bg/konkurs.html`: title беше 74 знака → предложение: „Конкурс: QR меню 3 месеца безплатно | SmartMenuKJ“ (49) — през мениджъра.
6. Още текст: about (172 думи) и portfolio (207 думи) са тънки; services ~80 думи на услуга. Факти от собственика за проекти в портфолиото.
7. Линкове: Instagram/TikTok/YouTube био → `https://www.smartmenukj.com/bg/` (през мениджъра към Плочко); местни каталози (собственикът).

## 12.11.2026 — M-1112-17 — EN/TR на 3-те нови BG статии
- Вече направено вчера (M-1111-38/41): `seo/articles/en/{small-business-website-checklist,3d-printing-what-can-be-made,slow-computer-7-causes}.md`, `seo/articles/tr/{isletme-web-sitesi-neler-olmali,3d-baski-neler-yapilabilir,yavas-bilgisayar-7-neden}.md`, hreflang таблица в `seo/articles/README.md`.
- Проверено на живо 12.11: 6/6 → 200, всяка с 5 hreflang реда. TR „3d-baski“ и „isletme-web-sitesi“ вече индексирани; EN — „открити“, чакат обхождане.

## 12.11.2026 — M-1112-14 — постове за Google Business Profile → `seo/gbp-posts.md`
- Първи пост: конкурсът „QR меню 3 месеца безплатно“ (≈720 зн.), бутон → /bg/konkurs.html; фактите дословно от живата страница (срок 19.11 23:59, теглене 20.11).
- Отсега всеки понеделник: нов пост в отчета (записано в SEO.md, Цикъл т. 4).
- Title на /bg/konkurs.html вече е скъсен на живо (49 зн.) → т. 8 от „Следващи стъпки“ ✅.

## 12.11.2026 10:17 — цикъл
- **Индексирани: 46/62** (вчера сутрин 15/43). Не още: 6 EN статии (открити, не обходени), `/blog/` и `/bg/konkurs.html` (още непознати), TR „yavas-bilgisayar“ (обходена, не индексирана). `/bg/faq.html` — индексирана.
- Performance 28 дни: 11 кликa, 21 показвания, ср. позиция 5.3 — почти само по името (началната поз. 1.6); заявки още няма в отчета (данните закъсняват 2–3 дни, страниците са нови).
- site_shot: /bg/konkurs.html, /bg/faq.html, /bg/blog/baven-kompyutar-7-prichini.html — 0 проблема. H1 на EN/BG/TR вече с Кърджали → т. 5 ✅.
- Забелязано: `contact.html?service=smarthome` има показване в Google; canonical сочи към `contact.html` — ок, нищо не правя.
- Поука на деня: вчера `git pull --rebase` в `&&` верига спря на незаписан telegram.json и commit-ът излезе с грешно съдържание → сега винаги `git add seo` преди pull.

## 11.11.2026 ~20:00 — M-1111-48 — отчет на деня в групата
- На живо (програмистът): /bg/faq.html, /blog/, /tr/blog/, новите BG статии → sitemap 61 адреса; sitemaps-submit пуснат.
- Утре: проверка на живо на FAQ + статиите (site_shot), inspect-sitemap (61), `gsc.py performance` за позиции.

## 11.11.2026 — M-1111-44 — обща FAQ страница `/bg/faq.html` → `seo/faq-page.md`
- 59 въпроса от 6-те услуги + 6-те статии → 33 без дублите, в 7 групи (общи + 6 услуги), под всяка група линк към услугата и статията. Текстовете дословно от източниците (сливани само при два отговора на един въпрос).
- Указания: шаблон, FAQPage + BreadcrumbList JSON-LD (същият текст като видимия), „Въпроси“ във футъра (BG), линкове от contact/services, sitemap.

## 11.11.2026 — M-1111-42 — 10 безплатни каталога → `seo/citations.md`
- Google Business Profile, Bing Places, Apple Business Connect (BG поддръжка непотвърдена), OpenStreetMap, Firma.bg, Firm.bg, bgbiznes.eu, iBusiness.bg, Favzz, BGfirma (+ Invest Bulgaria резерва). Готов текст: име, адрес, телефон, сайт, категории, описание BG/EN ~250 зн. Имейл и работно време — от собственика.
- Условията са от търсене в мрежата; сайтовете на каталозите не са отворени (мрежата на средата). Регистрира собственикът.

## 11.11.2026 15:01 UTC — M-1111-38 / M-1111-41 — Готово
- ✅ Новите title + description на живо: **15/15** съвпадат с seo/meta-update.md, og:title/og:description също 15/15 (UA Googlebot, без кеш). site_shot `/bg/`: 0 проблема.
- ✅ sitemaps-submit: Google прочете sitemap-а в 14:54 UTC — **60 адреса**, 0 грешки (броячът „indexed“ на GSC се обновява след дни; меря с inspect).
- Индексирани (inspect днес): `/bg/`, `/bg/3d-pechat-kardzhali.html`, `/bg/kompyutaren-servis-kardzhali.html`. Следва: inspect-sitemap след 2–3 дни.

## 11.11.2026 ~15:00 UTC — M-1111-38 (частично) — Search Console + проверка на title/description
- ✅ sitemaps-submit (живият sitemap: 60 адреса; GSC още показва последното четене 12:47 — 43, pending).
- ✅ inspect: `/bg/` — **индексирана** (обходена 13:26 UTC), `/bg/3d-pechat-kardzhali.html` — **индексирана** (12:48), `/bg/kompyutaren-servis-kardzhali.html` — **индексирана** (13:15). Сутринта и трите бяха „не е известен“ / „открита – не е индексирана“.
- ⏳ Новите title/description (M-1111-37) **още не са на живо**: 0 от 15 съвпадат с seo/meta-update.md (проверено с UA на Googlebot). Проверявам пак, щом мениджърът потвърди качването.

## 11.11.2026 — M-1111-35 — нови title/description на 15-те стари страници → `seo/meta-update.md`
- Старите: title 45–116 знака (11 от 15 над 60), description 158–222 (всички над 155) → Google ги реже. Новите: title 44–57, description 131–154; услуга + град отпред, марката накрая.
- Остава: след като програмистът ги качи → проверка на живо + `gsc.py sitemaps-submit`.

## 11.11.2026 — M-1111-33 — EN и TR версии на 6-те статии (12 файла)
- `seo/articles/en/` (733–888 думи) и `seo/articles/tr/` (569–763 думи): естествен текст, местни думи (Kardzhali/Kırcaali, както на сайта), title ≤60, description ≤155, по 5 FAQ, линкове към EN/TR страниците на услугите и към другите статии на същия език (всяка статия получава ≥3 от статиите + списък + услуга).
- Проверено: всички вътрешни линкове сочат към живи адреси от sitemap-а или към новите статии; frontmatter с `bg`/`en`/`tr` за hreflang.
- Таблица bg↔en↔tr + указания за програмиста (hreflang, sitemap +14, футър „Blog“ на EN/TR): `seo/articles/README.md`.

## 11.11.2026 — M-1111-30 — 3 нови статии за блога (BG) в seo/articles/
- `sait-za-zavedenie-kakvo-tryabva-da-ima.md` (~895 думи), `3d-pechat-kakvo-moje-da-se-napravi.md` (~740), `baven-kompyutar-7-prichini.md` (~800). Title ≤60 и description ≤155 с „Кърджали“, FAQ (5 въпроса), линкове към услугите и към другите статии.
- Само факти от страниците за услуги/сайта (SSD, памет, вируси, принтери, бекъп; PLA/PETG/ABS/TPU, сканиране, малки серии, проектът със скобата; mobile-first, резервации, Firebase, домейн, поддръжка, проектът със сайта за резервации). Общите съвети (Task Manager, прах, пълен диск) са без числа и обещания.
- Указания за програмиста + линковете за ≥5 входящи на статия: `seo/articles/README.md` (раздел M-1111-30).

## 11.11.2026 — M-1111-27 — проверка след M-1111-25 (PR №22): вътрешни линкове преди → след
Обходени 43-те адреса на живо; „рендирано“ = Chromium с UA на Googlebot (футърът е от JS; обикновен браузър без бисквитка се пренасочва към /bg/ — по замисъл, ботовете не).
| Страница | преди | след, HTML | след, рендирано |
|---|---|---|---|
| Услуги EN (×6) | 3–6 | 7 | **12** |
| Услуги BG (×6) | 3–9 | 7–10 | **16** |
| Услуги TR (×6) | 3–6 | 7 | **12** |
| /bg/blog/ | 3 | 5 | **16** |
| Статии (×3) | 2 | 3 | 3 |
✅ Цел ≥10 изпълнена за всичките 18 услуги (с рендиране); 3D печат: 3 → 12/16. Само в HTML (без JS) — 7, т.е. футърът носи 5–6.
✅ 67 вътрешни адреса от рендираните страници → всички 200, няма счупени. Футърът за Googlebot е на верния език (EN services → web-design-kardzhali.html…).
✅ sitemaps-submit пак.
Остава: статиите имат по 3 входящи → линк от още 1–2 свързани страници (напр. QR статия от сайтове, камери статия от умен дом); inspect-sitemap след 2–3 дни.

## 11.11.2026 — M-1111-24 — вътрешни линкове към 18-те страници за услуги + блога (обходени всички 43 адреса от sitemap-а на живо)
**Входящи линкове в HTML (без хедър/футър, те се рисуват с JS):**
| Услуга | EN | BG | TR |
|---|---|---|---|
| QR меню | 4 | 6 | 4 |
| Сайтове | 6 | 7 | 6 |
| Камери | 6 | 9 | 6 |
| Умен дом | 5 | 8 | 5 |
| 3D печат | **3** | **3** | **3** |
| Сервиз PC | 4 | 4 | 4 |

Блог: `/bg/blog/` — 3 (само „Начало“ от самите статии) + футърът (JS, само BG); всяка статия — **2** (блога + 1 услуга).
Слабо: 3D печат и сервиз; about/contact/portfolio → 0 линка към услугите (×3 езика); `/bg/` и `/bg/services.html` нямат линк към блога в HTML; футърът (`js/chrome.js` р. 231–236) на ВСИЧКИ страници води към `services.html#…` вместо към новите страници.

**Готови промени (за програмиста, repo SW1TF0/SmartMenu):**
1. **`js/chrome.js` — футърът към новите страници (най-голям ефект: +6 линка на всяка страница × 3 езика).** Над функцията на футъра добави:
```js
const SVC_PAGES = {
  en: { web: "web-design-kardzhali.html", print3d: "3d-printing-kardzhali.html", smarthome: "smart-home-kardzhali.html", cameras: "cctv-kardzhali.html", menu: "qr-menu-kardzhali.html", pc: "computer-repair-kardzhali.html" },
  bg: { web: "izrabotka-na-saitove-kardzhali.html", print3d: "3d-pechat-kardzhali.html", smarthome: "umen-dom-kardzhali.html", cameras: "videonablyudenie-kardzhali.html", menu: "qr-menu-kardzhali.html", pc: "kompyutaren-servis-kardzhali.html" },
  tr: { web: "web-sitesi-kircaali.html", print3d: "3d-baski-kircaali.html", smarthome: "akilli-ev-kircaali.html", cameras: "guvenlik-kamerasi-kircaali.html", menu: "qr-menu-kircaali.html", pc: "bilgisayar-servisi-kircaali.html" },
};
const svcHref = (k) => (SVC_PAGES[document.documentElement.lang] || SVC_PAGES.en)[k];
```
и в р. 231–236 `href="services.html#web"` → `href="${svcHref("web")}"` (същото за print3d, smarthome, cameras, menu, pc). Пътищата остават относителни като досега (статиите имат `<base href="/bg/">`). Провери логиката на р. 113–150 (скриването на бизнес съдържание при `services.html#menu`), за да не скрие новите линкове.
2. **`tools/build-service-pages.mjs` — статичен блок „Други услуги в Кърджали“** преди CTA на всяка от 18-те страници: линкове към другите 5 услуги на същия език (в HTML, не в JS). Текстове:
   - BG: „QR меню за заведения“, „Изработка на сайтове“, „Видеонаблюдение и камери“, „Умен дом и автоматизация“, „3D печат“, „Компютърен сервис и принтери“ (+ на страниците с тема: „Прочетете още: <заглавие на статията>“).
   - EN: „QR menus for restaurants“, „Website design“, „CCTV & security cameras“, „Smart home automation“, „3D printing“, „Computer & printer repair“.
   - TR: „Restoranlar için QR menü“, „Web sitesi tasarımı“, „Güvenlik kamerası sistemleri“, „Akıllı ev otomasyonu“, „3D baskı“, „Bilgisayar ve yazıcı servisi“.
   Покрива всички липсващи кръстосани линкове (днес: умен дом → липсват 4; всяка друга → по 2: QR→3D, сервиз; сайтове→умен дом, 3D; камери→3D, сервиз; 3D→QR, камери; сервиз→QR, умен дом — еднакво на 3-те езика).
3. **`bg/index.html`** — преди контакта: `<a href="blog/">Блог: съвети за QR менюта, камери и умен дом</a>`.
4. **`bg/services.html`** — под секциите: `#menu` → `blog/qr-menu-kak-raboti.html` „QR меню: как работи и какво печели заведението“; `#cameras` → `blog/videonablyudenie-predi-montazh.html` „Видеонаблюдение за дом и бизнес: какво да знаете преди монтажа“; `#smarthome` → `blog/umen-dom-ot-kade-da-zapochnete.html` „Умен дом: от какво да започнете“; накрая „Блог“ → `blog/`.
5. about/contact/portfolio — покриват се от т.1; по желание в `about.html` (×3) едно изречение с линкове към 6-те страници.

Проверка след пускане: обхождане на 43-те адреса пак → всяка услуга ≥ 10 входящи; `site_shot.js` без счупени линкове; `gsc.py sitemaps-submit`.

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
