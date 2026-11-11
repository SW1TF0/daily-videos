# Досие: SEO агентът

Мениджърът го попълва и обновява. Само факти с дата и източник.

## Какво прави (от seo/SEO.md)
- SEO на сайтовете на собственика, първо smartmenukj.com (repo SW1TF0/SmartMenu): техническо SEO, съдържание (само факти), ключови думи, предложения за Search Console и Google Business Profile.
- Задачи само от мениджъра (`task seo`). Цикъл веднъж дневно в 10:17 + слушател; седмичен отчет в понеделник. Дневник `seo/log.md`, думи `seo/keywords.md`.
- Не прави: ключове, плащания/реклами, черно SEO, код на агентите, съдържание в мрежите.

## Как се справя (дневник)
- 11.11.2026 13:00: създаден от мениджъра по молба на собственика. Чака: бот в Telegram (собственикът го прави), токен `TELEGRAM_SEO_BOT_TOKEN`, среда, сесия, насрочена задача; профил `--as seo` в telegram.py (задача към програмиста).

- 11.11.2026 13:02: създадена среда „SEO - smartmenukj“ (`env_01ReuHqVvmgjk37aHk98vNjr`; api.telegram.org, smartmenukj.com, www.smartmenukj.com; repo daily-videos). Чака: името на бота и `TELEGRAM_SEO_BOT_TOKEN` от собственика, M-1111-08 (профил `--as seo`). После: `create_session` в средата + `create_trigger` (CRON_TZ=Europe/Sofia 17 10 * * *) + запис тук.

- 11.11.2026 13:09: ботът е @seoswitfo_bot, токенът е в средата. Сесия `session_015VXfwyUiTt9ugEsuB7XF6F`, цикъл `trig_01HGPr3bdMi6PNoKTjVPCf4b` (10:17 всеки ден). Първа работа: одит на smartmenukj.com (само преглед) + `seo/keywords.md`. M-1111-08 (профил `--as seo`) — с приоритет при програмиста.

- 11.11.2026 13:12: първи одит (seo/log.md, seo/keywords.md). Основата добра; проблеми: няма страница по услуга, общ H1, тънки about/portfolio, непълен JSON-LD. Блокери: KeyError 'seo' (чака M-1111-08); add_repo SmartMenu с push отказан от auto mode → има само четене, промени по сайта засега през програмиста или PR.

- 11.11.2026 13:15: `--as seo setup` работи, представи се в групата, слушателят върви.

- 11.11.2026 14:05: add_repo SmartMenu с push пак отказан от auto mode ("Access Added As A Means") → промените по сайта минават през програмиста (блогът → M-1111-19). Собственикът иска автоматично индексиране и Business Profile: план — service account за Search Console (GOOGLE_SA_JSON + хостове в средата), инструмент src/gsc.py (M-1111-20). GBP: създаване/потвърждение ръчно от собственика, API след одобрение от Google.

## Въпроси и отговори

## Силни страни / слабости / идеи
