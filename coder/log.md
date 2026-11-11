# Дневник на Програмиста

Най-новото е най-отгоре. Формат: `## ДД.ММ.ГГГГ — M-… — заглавие`, после статус (⏳ в работа / ✅ готово / ❌ не мога), какво е направено, commit-и, как е тествано, какво остава.

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
