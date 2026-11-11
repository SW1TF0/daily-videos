# Дневник на Програмиста

Най-новото е най-отгоре. Формат: `## ДД.ММ.ГГГГ — M-… — заглавие`, после статус (⏳ в работа / ✅ готово / ❌ не мога), какво е направено, commit-и, как е тествано, какво остава.

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
