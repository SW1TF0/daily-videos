# Дневник на Програмиста

Най-новото е най-отгоре. Формат: `## ДД.ММ.ГГГГ — M-… — заглавие`, после статус (⏳ в работа / ✅ готово / ❌ не мога), какво е направено, commit-и, как е тествано, какво остава.

## 13.11.2026 — M-1113-08 — WebP автоматично при сглобяване на smarthomekj
✅ PR https://github.com/SW1TF0/smarthomekj/pull/25 (на живо): scripts/product-images.mjs (prebuild/predev/pretypecheck; Firestore REST → sharp → public/img/products/<sha16>.webp + src/data/product-images.json, gitignored; грешка → оригиналът, без да пада build); images.ts чете картата; preconnect махнат; sharp devDependency. Тест: локално 17 копия (през прокси: NODE_USE_ENV_PROXY=1), fallback при изтрито копие; Actions лог „17 WebP copies“. img/shop/ в SmartMenu вече не се ползва (може да се махне).

## 13.11.2026 — M-1113-07 — скорост на smarthomekj
✅ SmartMenu#43 (img/shop/*.webp, 2,2 MB PNG → 221 KB) + smarthomekj#24 (lib/images.ts fastImage → www + webp, ProductImage с onError към оригинала, preconnect). Мерене Playwright 390 px, CPU×4, жив каталог: снимки shop 1129→122 KB, продукт 196→24, BF 581→65; CLS ≤0,011; JS ~290 KB gzip (Firebase) — предложение, не е пипано. Pages + Vercel success.

## 13.11.2026 — M-1113-03 — страница „линк в био“
✅ PR https://github.com/SW1TF0/SmartMenu/pull/42 (сам, на живо): links.html (самостоятелна, css/style.css + малък inline стил, noindex follow); бутони с data-until (конкурс 20.11, Черен петък 1.12); utm_* от адреса → към линковете (+ utm_campaign=links). GitHub Pages отваря /links без .html. Playwright 390 px локално + на живо — 0 грешки.

## 13.11.2026 — бележка: нощното пресглобяване на smarthomekj
⚠️ cron в deploy.yml (M-1112-21) не тръгна в 22:05 UTC: schedule работи само на клона по подразбиране (claude/smarthomekj-website-7qunc8), а сайтът е от main. Нужно: собственикът да смени default branch на main. Черният петък не е засегнат (в браузъра).

## 12.11.2026 — M-1112-32 — портфолиото една под друга на телефон
✅ PR https://github.com/SW1TF0/SmartMenu/pull/41 (сам, на живо): само #projGrid в мобилното правило → grid 1 колона (другите .grid-3 редове — както са); ?v=20261112i. Chrome 360/390/414 — ок, филтърът (pc → 3 карти) ок; site_shot на живо 4 — 0.

## 12.11.2026 — M-1112-31 — портфолиото на телефон (спешно)
✅ PR https://github.com/SW1TF0/SmartMenu/pull/40 (сам, на живо): .proj-photo img и .proj-ba img — position absolute, inset 0 (Safari не оразмерява img по aspect-ratio кутията); .proj-ba → flex; на телефон .proj-photo 2:1 като другите. Chrome 360/390/414 — ок; WebKit няма в средата → чака потвърждение от собственика. Хоризонталният ред на телефон е старият дизайн (8df5f68, 21.10).

## 12.11.2026 — M-1112-30 — казус за старческия дом в блога
✅ PR https://github.com/SW1TF0/SmartMenu/pull/39 (сам, на живо): content/bg/blog/kazus-…md (част 2 от seo/cases дословно); генераторът: статия без FAQ → без FAQPage/без раздел; линкове от портфолиото (folio.r2.more), сервиза, „бавен компютър“; sitemap; ?v=20261112g. site_shot локално 6 + на живо 3 — 0.

## 12.11.2026 — M-1112-29 — бутоните към постовете + „Преди/След“
✅ PR https://github.com/SW1TF0/SmartMenu/pull/38 (сам, на живо): content/{bg,tr}/pages/konkurs.md → линкове към reel/видеата; portfolio: .proj-ba (2× 3:4 с figcaption), portfolio_images.py --half, care-home.webp махнат; ?v=20261112f. site_shot локално + на живо — 0.

## 12.11.2026 — M-1112-27 — портфолио с реални проекти
✅ PR https://github.com/SW1TF0/SmartMenu/pull/37 (сам, на живо):  шаблон (img/portfolio/<име>.webp + услуга + град + текст; data-i18n-alt в build-langs и i18n.js), tools/portfolio_images.py (1200 px WebP, без EXIF/GPS), карти: „Мрежа и техника за старчески дом“ (текстът на собственика) и „Два сглобени компютъра“. Снимките от Плочко (assets/portfolio/): network-switch-after → care-home.webp, pc-build-2 → pc-build.webp; 3:2, 43–46 KB, без EXIF. site_shot локално 4 + на живо 3 — 0.

## 12.11.2026 — M-1112-24 — марката (seo/brand-plan.md)
✅ PR https://github.com/SW1TF0/SmartMenu/pull/36 (сам, на живо): alternateName масив в LocalBusiness + WebSite; hero.eyebrow „SmartMenuKJ · Smart Menu <град>“ (3 езика); about.title + нов абзац about.brand (data-i18n-html, линкове към услугите на езика); „(смарт меню)“ в content/bg/qr-menu.md. site_shot локално 7 + на живо 4 — 0.
Бележка: първата медия от собственика (13:40 BG) е изядена преди кода на M-1112-22 → помолих да я прати пак; `media get` вече приема и папка.

## 12.11.2026 — M-1112-22 — медия от собственика за Плочко (#плочко)
✅ src/telegram.py: capture_media() при всяко четене на бота на Плочко (`tasks` и `wait`) → data/media.jsonl (file_id, file_unique_id, вид, размер, текст, дата; само от собственика, само в групата, с #плочко; албумите — по тага на един от елементите; дубликатите — по file_unique_id). `media [all]`, `media get <n|file_id|all>` → out/media/ (getFile, до 20 MB; по-голям → съобщение да го прати по-късо/като файл; токенът не се показва). build.py: карти photo/clip и hook_photo с локален `src` (out/media/…), clip взима първите `secs`; липсващ файл → сцена + бележка. CLAUDE.md: в „Сценарий“ и „Telegram“.
Тест без мрежа: 10 фалшиви update-а (тагове, чужд автор, друг чат, PDF, само текст, албум, файл-снимка, видео 30 MB) → 5 записа, повторно 0, coder 0; get с фалшив getFile/curl; resolve_media със снимка, видео (120 кадъра за 4 с) и липсващ файл.

## 12.11.2026 — M-1112-21 — SEO на smarthomekj (по одита)
✅ PR https://github.com/SW1TF0/smarthomekj/pull/23 (сам, SEO, на живо): src/lib/catalogue.ts (Firestore REST runQuery active==true при build, резерва starterProducts), продуктовите страници/sitemap от него, нощно пресглобяване (deploy.yml cron 22:05 UTC); /shop/c/[category] за категориите с продукти (6), текстове по реалните продукти; Product/Offer + BreadcrumbList JSON-LD в server page (lib/product-seo.ts); productHref винаги /shop/<slug>/, global-not-found пренасочва нови продукти към ?p=; ShopGrid с initial каталог (статичният HTML с реалните продукти).
Тест: tsc, lint, build с живия каталог (18×3 продукта, 6×3 категории, sitemap 117), Playwright; Vercel + Pages success.
Наученото: живият каталог (Hama/HIKVISION/iRobot) е съвсем различен от seed-а — одитът е писан по seed-а; firestore.googleapis.com е достъпен от средата (с node fetch; браузърът — през прокси).

## 12.11.2026 — M-1112-16 — OG снимки за страниците на услугите
✅ PR https://github.com/SW1TF0/SmartMenu/pull/35 (сам, на живо): tools/make-og-images.mjs (Playwright, Inter latin/latin-ext/cyrillic, иконите от js/icons.js, имената от SVC_NAMES/UI — вече export) → img/og/<lang>-<service>.jpg, 29–44 KB; shell() приема image → og:image + width/height/alt + twitter:card/twitter:image; build спира без снимка; README.
Тест: само 18-те страници се промениха; 18/18 снимки 200 на живо; site_shot локално 4 + на живо 3 — 0.

## 12.11.2026 — M-1112-11 — конкурс: бутони, правило за победителя, TR версия
✅ PR https://github.com/SW1TF0/SmartMenu/pull/34 (сам, на живо): бутони „Участвай“ към профилите (IG/TikTok/YouTube); правилото за победителя от contest/ (2e7fb59); „област Кърджали“ в увода и стъпка 2; content/tr/pages/konkurs.md → /tr/konkurs.html, hreflang по `key:`, sitemap, TR банер + футър (PROMO_PAGES.tr). Генератор: редове „=> [текст](url)“ = бутони; стъпките без двойна точка (клас legal-steps — „steps“ вече е зает от началната!). ?v=20261112d.
Тест: site_shot локално 5 + на живо 3 — 0. Остава: линк към самия пост, когато Плочко го даде.

## 12.11.2026 — M-1112-10 — проверка на анимациите на живо
✅ smartmenukj.com на живо (?v=20261112c): Playwright през прокси — тема с View Transition (1 извикване), при reducedMotion: reduce — 0 извиквания и transition 1e-05s; видео в групата. smarthomekj (main 220809c, Pages+Vercel success): smarthomekj.eu недостъпен → проверена сглобката на commit-а: page-in 0.45s, CountUp 7→14 / 1→2, reduce → без анимация. Поправки не бяха нужни.

## 12.11.2026 — M-1112-09 — конфликт в PR #32
✅ merge на main в coder/M-1112-07-motion; конфликт само в 404.html (?v=) → версията от main + нов печат ?v=20261112c + build-langs; разлика спрямо main: само CSS-ът на анимациите и версиите. site_shot 5 — 0. PR #32: mergeable.

## 12.11.2026 — M-1112-08 — 404 на 3 езика + title на конкурса
✅ PR https://github.com/SW1TF0/SmartMenu/pull/33 (сам, на живо): 404.html — езикът от /bg/ или /tr/ в адреса (иначе запазения/по подразбиране), линкове към 6-те услуги, всички услуги, блога и FAQ (BG) от SVC_PAGES (вече export в chrome.js); <base> сочи папката на езика, за да са верни линковете в хедъра/футъра; смяна на езика → същият адрес в другата папка. Title на /bg/konkurs.html = „Конкурс: QR меню 3 месеца безплатно | SmartMenuKJ“.
Тест: Playwright с локален сървър, който връща 404.html (3 адреса: верен език, всички линкове 200, превключване BG→TR→EN→BG); site_shot 0.
Наученото: 404.html стои в корена, а footer-ът е с относителни линкове за папката на езика → на /bg/ 404 линковете чупеха; оправено с <base>.

## 12.11.2026 — M-1112-07 — анимации и преходи (два сайта)
✅ собственикът ги сля (12.11), проверени на живо в M-1112-10: PR https://github.com/SW1TF0/smarthomekj/pull/22 и https://github.com/SW1TF0/SmartMenu/pull/32.
smarthomekj: app/[locale]/template.tsx (страницата влиза при навигация, fill backwards), CountUp за статистиките, значка на количката, меню на телефон, hover само при (hover:hover), натискане на плочки, бутон/шеврон. Тъмна тема няма → смяна на тема не е приложима.
SmartMenu: вече имаше тема с кръг, reveal, броячи, hover; добавено: ::view-transition-old/new(root) при смяна на страница, натискане на хапове/икони, шеврон; ?v=20261112b.
Тест: tsc/lint/next build; site_shot 4 — 0; записи с Playwright recordVideo → mp4 в групата.

## 12.11.2026 — M-1112-04 — YouTube в sameAs + „Черен петък“ за smarthomekj
✅ 1) PR https://github.com/SW1TF0/SmartMenu/pull/31 (на живо): https://www.youtube.com/@smartmenukj в sameAs на началните EN/BG/TR; site_shot 3 — 0.
✅ 2) PR https://github.com/SW1TF0/smarthomekj/pull/21 — СЛЯТ, на живо (собственикът: −10% на всичко, 13.11 00:00–30.11 23:59). Отстъпката е в loadProducts (браузъра) → магазин/продукт/калкулатор/поръчка еднакво, сама почва и спира; количката се преизчислява при зареждане; админът приема промо цената; цена × 0,9 надолу до 10 ст. Тест с часовник 12.11/13.11/01.12 + количка 128,90→116,00→128,90. Важно: в smarthomekj клонът по подразбиране е claude/smarthomekj-website-7qunc8, а сайтът се пуска от main (GitHub Pages + Vercel) — PR-ите към main.
Първоначално (преди решението): PR с места [ОТСТЪПКА]: Next.js (static export). /[locale]/black-friday/ (таймер до 27.11 00:00 +02:00, после до края, после „приключи“), плочки по категориите на магазина, условия; лента с таймер на началната, скрива се след края; речниците bg/en/tr; sitemap. Цени/условия/край — само в src/lib/black-friday.ts (null = жълто [ОТСТЪПКА]).
Тест: tsc, next lint (само старото предупреждение), next build; Playwright телефон/компютър на 4 страници — без грешки и скрол.
Остава: цените, условията и краят от собственика → попълване → сливане. smarthomekj.eu не е достъпен от средата — домейнът не е потвърден.
Наученото: Reveal анимациите се показват само при скрол — за пълни снимки скролирай страницата преди снимката; networkidle не идва (Firebase) — чакай load.

## 12.11.2026 — M-1112-03 — уточнение: наградата е 3 месеца безплатно
✅ PR https://github.com/SW1TF0/SmartMenu/pull/30: увод, правилото „Награда“ (дословно от contest/ 11a7f92), title/description/H1 и банерът на /bg/. Тест: „Правила“ ред по ред == източника; site_shot 2 — 0.

## 12.11.2026 — M-1112-03 — страница за конкурса /bg/konkurs.html
✅ PR https://github.com/SW1TF0/SmartMenu/pull/29 (слях го сам, на живо): content/bg/pages/konkurs.md (кратката част + „Правила“ дословно от contest/2026-11-qr-menu.md) → bg/konkurs.html; банер „🎁 Конкурс до 19.11…“ над заглавието на /bg/ и „Конкурс“ във футъра на BG; от 20.11 js/chrome.js ги скрива сам (until), страницата остава. Генераторът вече прави и обикновени страници от content/<lang>/pages/*.md (front matter: until/banner/footer; footer изисква запис в PROMO_PAGES в chrome.js — сглобяването проверява). Sitemap 62; ?v=20261112.
Тест: сглобяване преди/след — в HTML разлика само банерът и версията; двойно сглобяване = същото; site_shot локално 5 — 0, на живо — виж Готово.

## 12.11.2026 — M-1112-01 — изходящи лийдове и sameAs
✅ 1) src/manager.py status_sales: лийдовете с direction "out"/"outbound" или source, започващ с outreach/scout, не се броят в „Запитвания без отговор“; брои ги отделно `outreach_not_sent` (direction "in" печели над source). Commit 860ed2f. Тест: 7 случая на outbound_lead + status на живите sales/leads.jsonl → new 0, outreach_not_sent 3, без alert.
2) PR https://github.com/SW1TF0/SmartMenu/pull/28: TikTok https://www.tiktok.com/@smartmenukj в sameAs на началните EN/BG/TR (възелът е LocalBusiness — подтип на Organization, отделен Organization не трябва). YouTube липсва: адресът на канала го няма в repo-тата, а youtube.com е блокиран от мрежата на средата → нужен е линкът (Плочко: `social.py accounts`).
Тест: JSON-LD парснат на 3-те страници; site_shot локално 3 — 0.

## 11.11.2026 — M-1111-47 — отчет на деня
✅ Отчетът за 11.11 е в групата (22 задачи, числата за сайта, какво спъва, предложения за утре). Контейнерът беше рестартиран около 17:50 — repo-тата са цели, работата продължава.

## 11.11.2026 — M-1111-45 — FAQ страница /bg/faq.html
✅ PR https://github.com/SW1TF0/SmartMenu/pull/27 (слях го сам, на живо): content/bg/faq.md (без указанията за програмиста) → bg/faq.html през генератора (parseFaqPage/renderFaqPage), FAQPage (33) + BreadcrumbList; линк под формата на bg/contact.html, на bg/services.html, „Въпроси“ във футъра само на BG; sitemap 61; ?v=20261111f.
Тест: видимите въпроси/отговори == JSON-LD (скрипт); site_shot локално 4 + на живо 3 — 0; двойно сглобяване = същото.
Наученото: content/<lang>/*.md се четат като страници на услуги → faq.md изрично изключен; в i18n.js EN и TR имат еднакъв ред "footer.blog": "Blog" — редакция по низ трябва да брои срещанията.

## 11.11.2026 — M-1111-40 — профил --as scout и status_scout
✅ src/telegram.py --as scout (TELEGRAM_SCOUT_BOT_TOKEN, scout/telegram.json, слушателят върви през деня и спи от ~21:57 (last_cycle 22:00, цикълът е в 11:13), думи „разузнавач(ът/а)“/„scout“ като цяла дума; ботът само от agents.json → scout.telegram, с предпазителя). manager.py status_scout: общите проверки + scout/prospects.jsonl (последният ред на id печели): общо, нови за 7 дни, по статус, чакащи за продажби (new и score ≥4); в неделя alert, ако за 7 дни са под 20. check „scout“ в регистъра.
Тест без мрежа в копие: без scout.telegram → отказ; setup/tasks/send; чужди токени → отказ; нощ от 21:58; разпознаване по име; status_scout с 4 фалшиви реда.

## 11.11.2026 — M-1111-37 — нови title/description на 15 страници
✅ PR https://github.com/SW1TF0/SmartMenu/pull/26 (слях го сам, на живо): текстовете от seo/meta-update.md (парснати програмно) — EN в HTML, BG/TR в BG_PAGES/TR_PAGES; og:title/og:description със същия текст.
Тест: 15 страници × 4 тага сравнени с таблицата — 0 разлики; site_shot 15 локално + 4 на живо — 0; на живо заглавията проверени с curl.

## 11.11.2026 — M-1111-34 — блогът на EN и TR
✅ PR https://github.com/SW1TF0/SmartMenu/pull/25 (слях го сам, на живо): content/{en,tr}/blog → /blog/, /tr/blog/ (+ списъци); преводите се връзват по BG адреса (bg: в front matter) → hreflang на 21 страници, превключвател към двойника; „Blog“ във футъра на всички езици; Read more/Devamını okuyun от EN/TR услугите; блог линк на EN/TR началните; TR FAQ заглавие „Sık“ или „Sıkça sorulan sorular“; sitemap 60 (блог записите се генерират от hreflang на страниците); ?v=20261111e.
Тест: site_shot локално 10 + на живо 5 — 0; sitemap↔страници 0; превключвател на езика (Playwright) на статия и на списъка; двойно сглобяване = същото.

## 11.11.2026 — M-1111-32 — още 3 статии в блога
✅ PR https://github.com/SW1TF0/SmartMenu/pull/24 (слях го сам, на живо): sait-za-zavedenie…, 3d-pechat-kakvo-moje…, baven-kompyutar-7-prichini; линкове в старите статии по README на SEO; „Още от блога“ под всяка статия (генераторът); всяка статия — 8 входящи; sitemap 46.
Тест: броене на входящите линкове в сглобения сайт; sitemap↔страници 0; site_shot локално 5 + на живо 5 — 0.
Бележка: изреченията в старите статии са само в SmartMenu content/bg/blog/ (не в seo/articles/) — SEO агентът редактира оттам нататък там.

## 11.11.2026 — M-1111-31 — достъпност и мобилна проверка
✅ PR https://github.com/SW1TF0/SmartMenu/pull/23 (слях го сам, на живо): контраст (seg бутон, eyebrow на сивите секции, бутонът в cta-band), подчертани линкове в текста, невидима зона за пръст 44px (lang, икони в хедъра) / 36px (breadcrumbs), футър h4→h3, mobile-cta-bar → <aside>, tabindex на хоризонталните списъци; ?v=20261111d.
Тест: axe-core 4.10 + свои проверки (≥44px, 360px скрол, фокус с Tab, lang) на 14 страници: 108 нарушения → 0 (локално и на живо); ефективната зона за докосване измерена с elementFromPoint; снимки преди/след; site_shot 0.
Остава (решение на собственика): бутоните 34–40px и иконите на мрежите — минават AA (24px), под 44px.

## 11.11.2026 — M-1111-29 — src/mail.py (ABV IMAP, само четене)
✅ src/mail.py: check, list [дни], read <uid>; ABV_IMAP_USER/ABV_IMAP_PASSWORD от env (никога не се печатат), imap.abv.bg:993 TLS, EXAMINE + BODY.PEEK (на сървъра нищо не се променя), прочетените uid в sales/mail.json, прикачените — само имената.
Тест: фалшив IMAP (imaplib.IMAP4_SSL подменен), 10 сценария: без данни, грешна парола, няма мрежа, check, list, read (текст+прикачен файл; само HTML), липсващ/невалиден uid, отбелязване; паролата не се появява в изхода.
❗ Мрежата: от облачна среда IMAP НЕ минава. Проверено: imap.abv.bg няма DNS в контейнера; CONNECT imap.abv.bg:993 през проксито → „200“ и веднага reset; README на проксито: само HTTPS на 443, суров TCP не се поддържа. POP3 (995) — същото.
💡 Друг път: Gmail (има Gmail connector) — в Gmail на собственика „Проверявай пощата от други профили“ (POP3 от ABV) или пренасочване в ABV към Gmail; агентът чете през Gmail connector-а. mail.py работи само с директна мрежа (компютърът на собственика / Remote Control).

## 11.11.2026 — M-1111-26 — профил --as sales и status_sales
✅ src/telegram.py --as sales (TELEGRAM_SALES_BOT_TOKEN, sales/telegram.json, last_cycle 16:41 — последният от двата цикъла 08:41/16:41, думи „продажби“/„sales“ като цяла дума; ботът само от agents.json → sales.telegram, с предпазителя). src/manager.py status_sales: общите проверки + лийдовете от sales/leads.jsonl (последният ред на id печели): нови, чакащи, спечелени, просрочени next_date → alerts. check „sales“ в регистъра.
Тест без мрежа в копие на repo-то: без sales.telegram → отказ; setup/tasks/send с верен токен; чужди токени → отказ само с getMe; нощ след 16:41; разпознаване по име; status_sales с 4 фалшиви реда.
Остава: собственикът — бот и TELEGRAM_SALES_BOT_TOKEN; мениджърът — sales.telegram в agents.json.

## 11.11.2026 — M-1111-25 — вътрешни линкове по одита на SEO (M-1111-24)
✅ PR https://github.com/SW1TF0/SmartMenu/pull/22 (слях го сам, на живо): футърът (js/chrome.js) → страниците на услугите по езика на страницата (таблицата се сверява с content/ при сглобяване); „Други услуги в Кърджали“ на 18-те страници; блог линк на /bg/; „Прочетете още“ + блог на /bg/services.html; ?v=20261111c.
Тест: site_shot локално 9 + на живо 7 страници — 0; футърните линкове проверени на живо на 3 езика (Playwright); двойно сглобяване = същото. Ходът беше прекъснат от лимита — продължих по съобщението на мениджъра.

## 11.11.2026 — M-1111-23 — src/manager.py: named_agent и failed_platforms
✅ named_agent търси като цяла дума (като telegram.py, M-1111-21; псевдонимите и с формите -ът/-ят/-а/-я/-та/-то, ботът с @ точно). status за Плочко: failed_platforms от data/videos.jsonl за 48 ч. (минус покритите от по-късно успешно качване на същото id) → `missing_platforms_48h` + alert „Не са качени в: …“.
Тест без мрежа: named_agent 11 случая, failed_platforms 6 случая — 0 провала; `manager.py status` на живите данни работи.
Пропуснато: включена ли е насрочената задача — в agents.json има само id-тата, а състоянието е само в list_triggers (мрежа/инструмент на мениджъра).

## 11.11.2026 — M-1111-21 — събуждане по име в src/telegram.py
✅ Имената на агентите се търсят като цяла дума (тирето е част от думата; „SEO - smartmenukj“ не се брои), за програмиста с формите „програмистът/програмиста“. Отговор на мениджъра към съобщение на собственика не буди агентите, освен с техния @ или задача „→ @бот“; отговор на собствено съобщение на агента още буди.
Тест: 19 случая / 30 проверки без мрежа — новият код 0 провала, старият 6 (точно бъговете от задачата). Наученото: при reload на модула, който чете --as от argv, argv трябва да се зададе преди всеки reload (първият тест мина като worker).
💡 manager.py named_agent има същото търсене по подниз (само етикет to_agent за мениджъра, не буди никого) — може да ползва telegram.named.

## 11.11.2026 — M-1111-20 — src/gsc.py (Google Search Console)
✅ src/gsc.py: sites, sitemaps-submit, sitemaps-list, inspect, inspect-sitemap, performance. Service account от GOOGLE_SA_JSON (JSON или път), JWT RS256 с openssl (ключът е на диска само за подписа: 0600 файл в /dev/shm, трие се веднага), токенът и assertion-ът минават към curl през stdin (-K -), никога в argv. Повторен опит при 429/5xx и мрежови прекъсвания, ясни съобщения при 403/404/липсващ ключ. Описано в seo/SEO.md.
Тест: фалшив curl, 14 сценария; фалшивият curl проверява подписа на JWT с истинския публичен ключ (грешен ключ → „Invalid JWT Signature“); 0 тайни в argv, 0 оставени файлове с ключ.
Остава: собственикът — GOOGLE_SA_JSON в средата „SEO - smartmenukj“, service account-ът като потребител в Search Console, хостове oauth2.googleapis.com и searchconsole.googleapis.com. После SEO агентът: `python3 src/gsc.py sites`.

## 11.11.2026 — M-1111-19 — блог /bg/blog/
✅ PR https://github.com/SW1TF0/SmartMenu/pull/21 (слях го сам, на живо): content/bg/blog/*.md → bg/blog/ (индекс + 3 статии), BlogPosting + FAQPage + Breadcrumb, <base href="/bg/"> (меню/футър/ресурси с относителни пътища), „Прочетете още“ от услугите, „Блог“ във футъра само на BG, sitemap 43, ?v=20261111b.
Тест: site_shot локално 8 + на живо 6 страници — 0; sitemap↔страници 0; футър/меню линкове проверени с Playwright.
Наученото: генераторът четеше ?v= само с цифри — суфикс „b“ даваше смесени версии (build-langs го хвана); поправено.

## 11.11.2026 — M-1111-15 — скорост на smartmenukj.com
✅ PR https://github.com/SW1TF0/SmartMenu/pull/20 (слях го сам, на живо): логата на партньорите WebP (141→32 KB), tools/minify-css.mjs + стъпка в deploy.yml, ?v=20261111. /bg/: 375→268 KB, LCP 1,78→1,56 с; страниците на услугите — 117 KB (без промяна, вече леки).
Тест: 10 снимки оригинален/минифициран CSS — идентични до пиксел; логата сравнени на живо/локално; site_shot 10 страници — 0.
⚠️ Минифицирането не стига до сайта: Pages е „Deploy from branch“ (тече и „pages build and deployment“) и последният deploy е от клона. Трябва собственикът: Settings → Pages → Source: GitHub Actions.
Наученото: модул с код на най-горно ниво се изпълнява и при import — моят тест минифицира работното копие (върнах го с git checkout); main кодът винаги зад проверка за argv[1].

## 11.11.2026 — M-1111-13 — EN и TR страниците за услугите
✅ PR https://github.com/SW1TF0/SmartMenu/pull/19 (слях го сам по правилото на собственика в CODER.md; на живо, site_shot 20 страници — 0 проблема): build-service-pages.mjs за EN/BG/TR от content/<lang>/*.md; hreflang по ключа service (x-default = BG); превключвателят води към двойника; „Научете повече“ и картите на трите езика (data-svc-page, защото EN services/index са източник за bg/tr); sitemap 39.
Тест: site_shot 23 страници — 0; sitemap↔страници 0 разминавания; превключвател EN/BG/TR (Playwright); двойно сглобяване = същото. PR №18 (BG) е слят.

## 11.11.2026 — M-1111-11 — 6 BG страници за услугите
✅ PR https://github.com/SW1TF0/SmartMenu/pull/18 (слят): текстовете на SEO агента в SmartMenu content/bg/*.md → tools/build-service-pages.mjs (шаблон = сглобения bg/services.html; build-langs.mjs го пуска, защото трие bg/). Service + FAQPage + BreadcrumbList JSON-LD, „Научете повече“ от bg/services.html, картите на bg/index.html, sitemap +6 (27).
Тест: site_shot 8 страници телефон+компютър — 0 проблема; JSON-LD се парсва; двойно пускане = същите файлове.
Остава: EN/TR (SEO агентът ги пише) → hreflang и превключвателят на езика. M-1111-10 (PR №17) е на живо — снимка в групата.

## 11.11.2026 — M-1111-10 — бързи SEO поправки на началната страница
✅ PR https://github.com/SW1TF0/SmartMenu/pull/17 (слят, на живо 11.11): H1 (EN/BG/TR, бизнес и дом) с услуги + Кърджали; FAQPage JSON-LD от FAQ секцията; build-langs.mjs превежда FAQ-а от речника, Service URL-ите → /bg/ и /tr/, inLanguage. Билдът гърми, ако JSON-LD FAQ-ът се разминава с FAQ-а на страницата.
Тест: JSON-LD се парсва (3 езика), 3 отрицателни теста, site_shot локално (телефон+компютър) — 0 проблема.

## 11.11.2026 — M-1111-08 — Telegram профил за SEO агента
✅ `src/telegram.py --as seo` (TELEGRAM_SEO_BOT_TOKEN, seo/telegram.json, думи „seo“/„сео“). Ботът се взима само от agents.json → seo.telegram: ако го няма, отказва (WrongBot), без да чете или праща. Предпазителят от M-1111-06 важи. last_cycle е 22:17, не 10:17: при 10:17 `listening` щеше да казва night веднага след цикъла и слушателят никога нямаше да тръгне. `src/manager.py`: общ status_bot_agent за coder и seo (задачи, introduced, последен commit в папката), `check: "seo"` в регистъра.
Тест: фалшив curl в копие на repo-то, 17 сценария (верен токен: setup/tasks/send/wait се събужда на задача за seo; чужд токен на Плочко/програмиста → отказ само с getMe; липсващ токен; невалиден; без seo.telegram; задачата за seo не стига до coder; coder/worker със seo токен → отказ; нощ 22:20; manager.py status). На живо: `--as coder setup` е ОК.

## 11.11.2026 — M-1111-07 — SEO/индексиране на smartmenukj.com
✅ PR https://github.com/SW1TF0/SmartMenu/pull/16 (слят от мениджъра; на живо проверено 11.11): sitemap.xml — 21 URL (7 страници × EN/BG/TR), lastmod 2026-11-04; robots.txt без Disallow за login/account/admin (те имат noindex, а блокът пречи на Google да го види); README бележка.
Проверено: canonical = loc, hreflang = <head>, без noindex (21/21); site_shot.js на живо — 0 счупени връзки, всички тагове налични. smartmenukj.com → 301 → www (CNAME), затова URL-ите остават с www.
Поправен src/site_shot.js: проверката на връзки (ctx.request) не минаваше през HTTPS_PROXY → всяка връзка излизаше ERR.
Средата: добавени хостове www.smartmenukj.com и smartmenukj.com. contact.js гърми само тук, защото www.gstatic.com (Firebase) е блокиран в средата.
Остава: собственикът изпраща sitemap-а в Google Search Console.

## 11.11.2026 — сесия session_015VXfwuyAsA2z8SSeZGi7SX — Telegram работи
✅ Новият `TELEGRAM_CODER_BOT_TOKEN` е на @itclaudeswitfo_bot (`--as coder setup`: в групата, чете всичко). Писах в групата. Нови задачи няма (M-1111-03, -04, -06 са свършени).

## 11.11.2026 — M-1111-06 — проверка на токена в src/telegram.py
✅ `token()` проверява с getMe (кеш в паметта и в /tmp по sha256 на токена, без самия токен), че токенът е на бота на профила от `manager/agents.json` (worker → plochko, coder → coder, manager → _manager; по подразбиране @dailyvideosswitfo_bot / @itclaudeswitfo_bot / @managerswitfo_bot). Чужд бот → `WrongBot` с ясна грешка преди getUpdates/send; `listening` казва off; `wait` спира веднага (не се върти в цикъла за повторни опити). Резервният режим на мениджъра (праща през бота на Плочко) е разрешен. При недостъпен getMe не блокира — проверява при следващото повикване.
Тест: фалшив curl, 13 сценария (чужд токен за tasks/setup/listening/wait/send за трите профила, верни токени, fallback, мрежова грешка, невалиден токен, кеш = 1 getMe). На живо: `--as coder tasks` → ясна грешка, само getMe, coder/telegram.json не е пипнат.

## 11.11.2026 — сесия session_015VXfwwpsbvCmo9qnPobzxk — грешен Telegram токен
❌ `TELEGRAM_CODER_BOT_TOKEN` е на @dailyvideosswitfo_bot (Плочко), а не на @itclaudeswitfo_bot — проверено с `--as coder setup`. Не пиша и не пускам слушател с него. Казано на мениджъра. Задачи: M-1111-03 и M-1111-04 са свършени.
💡 `setup`/`tasks`/`wait` в `src/telegram.py` да отказват, ако getMe върне чужд бот за профила.

## 11.11.2026 — M-1111-04 — 3-те риска в src/social.py
✅ а) При отказ на TikTok видеото излиза в другите мрежи, но редът има `failed_platforms: ["tiktok"]` и в stderr се печата `⚠️ FAILED on tiktok … (retry later: publish … tiktok)`; само TikTok + грешка → ok=false както преди. б) Idempotency-Key = id + sha1(файл(ове) + час + мрежи): същото качване = същата задача, ново сглобяване или нов час = нов ключ (и за каруселите). в) curl `--connect-timeout 20 --max-time 300`; curl грешка / не-JSON → ясно SystemExit; отговор-списък → `{"success": false, "error": …}`. CLAUDE.md стъпка 6 обновена.
Тест: py_compile + фалшив curl (ok, TikTok отказ, timeout, списък, HTML, нов час/нов файл → нов ключ, карусел). Остава: Плочко на живо.
💡 manager.py status може да брои `failed_platforms` като провал (код на мениджъра).

## 11.11.2026 — M-1111-03 — въпрос на мениджъра (TikTok 0 гледания, рискове)
✅ Отговорено в сесията на мениджъра (Telegram липсва: няма `TELEGRAM_CODER_BOT_TOKEN`). TikTok: privacy вече е PUBLIC (2270aa2), но каруселът how-it-works е излязъл след поправката и пак е с 0 гледания, а постовете имат URL. Най-вероятно е акаунтът (нов, 0 последователи, само API постове) или закъснели метрики → собственикът да провери в приложението. Рискове в social.py: тихо пропускане на TikTok при грешка с ok=true; Idempotency-Key = id връща стара задача; curl без timeout. Без промени в кода.

## 11.11.2026 — старт
✅ Агентът е създаден: инструкции `coder/CODER.md`, Telegram профил `--as coder` в `src/telegram.py`, регистриран при мениджъра (`manager/agents.json`, проверка `coder` в `python3 src/manager.py status`).
