"""Telegram group "Claude cluster" = the command centre of the agents. Three bots share it:
the worker (Плочко, daily videos), the coder (Програмистът, @itclaudeswitfo_bot) and the manager (@managerswitfo_bot),
who watches the agents and hands out tasks.

python3 src/telegram.py setup                    # find the group + people from recent messages -> data/telegram.json
python3 src/telegram.py allow <@username|id>     # who may give tasks (manager, owner)
python3 src/telegram.py send "<text>"            # post to the group
python3 src/telegram.py tasks                    # new messages addressed to us from allowed people (JSON lines); marks them read
python3 src/telegram.py reply <message_id> "<text>"   # answer a specific task message
python3 src/telegram.py photo <file.png|jpg> ["<caption>"] [reply_to]  # a picture to the group (e.g. a site before/after);
                                                 # too big or too tall for a photo -> sent as a file
python3 src/telegram.py media [all]              # Плочко: the owner's photos/videos posted with #плочко, not downloaded yet
                                                 # (all: every one); JSON lines with n, file_id, text (what it is), date
python3 src/telegram.py media get <n|file_id|all> [dir]  # download to out/media/ (or dir; never commit them: the repo is public); max 20 MB
python3 src/telegram.py listening                # yes | no | night | off  -> start `wait` (in the background) only on "no"
python3 src/telegram.py wait                     # listener: waits without AI cost, exits as soon as a message for us arrives
                                                 # exit 0 = new message for us, 2 = time is up, 3 = a turn reads Telegram itself

Add `--as manager` (e.g. `python3 src/telegram.py --as manager send "..."`) to act as the manager bot;
the manager reads the group with `python3 src/manager.py inbox`.
Add `--as coder` to act as the coder bot (`tasks`, `send`, `reply`, `listening`, `wait`, `setup` = check the bot),
`--as seo` / `--as sales` / `--as scout` the same for the SEO, sales and scout agents' bots (@username from manager/agents.json → <agent>.telegram).

Each token is checked with getMe (cached) against the agent's bot in manager/agents.json: a token of another bot
stops with a clear error before anything is sent or read.
Tokens come from the environment (TELEGRAM_BOT_TOKEN for the worker, TELEGRAM_MANAGER_BOT_TOKEN for the manager,
TELEGRAM_CODER_BOT_TOKEN for the coder, TELEGRAM_SEO_BOT_TOKEN for the SEO agent, TELEGRAM_SALES_BOT_TOKEN for the sales agent, TELEGRAM_SCOUT_BOT_TOKEN for the scout, set in each agent's environment settings) and are never printed or written to the repo.
A task from the manager names its agent in the header ("📋 Задача M-… → @bot"): only that agent takes it.
In a basic group message ids are per bot: refer to tasks by their id (M-1111-01) in the text, never by another bot's message id.

Media for Плочко: the owner posts photos/videos in the group with #плочко and a few words (what object, which service).
Every read of the worker bot (`tasks`, `wait`) records them in data/media.jsonl (only file ids and the text, never the
files); an album counts when one of its items carries the tag. Telegram lets bots download files up to 20 MB.

Listener: each bot has one reader at a time. `updates()` (used by `tasks` and by `manager.py inbox`) stops the
bot's listener first, so a turn that reads Telegram takes over; the agent starts `wait` again at the end of its turn.
The worker's listener marks read what is not for the worker (`tasks` would drop it anyway); the manager's listener
never takes anything, because `inbox` must still see the agents' Прието/Готово.
"""
import json, os, re, signal, subprocess, sys, time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG_PATH = os.path.join(ROOT, 'data', 'telegram.json')  # shared: chat_id, allowed, owner + the worker's offset
PROFILES = {
    'worker': {'env': 'TELEGRAM_BOT_TOKEN', 'state': CFG_PATH, 'last_cycle': (23, 23), 'names': ('плочко',)},
    # names are whole words; a regex may add the Bulgarian forms (програмистът, програмиста)
    'manager': {'env': 'TELEGRAM_MANAGER_BOT_TOKEN', 'state': os.path.join(ROOT, 'manager', 'telegram.json'), 'last_cycle': (22, 53)},
    'coder': {'env': 'TELEGRAM_CODER_BOT_TOKEN', 'state': os.path.join(ROOT, 'coder', 'telegram.json'), 'last_cycle': (22, 38),
              'names': ('програмист(?:ът|а)?',)},  # words in the manager's text that mean "this is for the coder"
    # one daily cycle at 10:17, but the listener chains itself through the day like the coder's: it sleeps from 22:17
    'seo': {'env': 'TELEGRAM_SEO_BOT_TOKEN', 'state': os.path.join(ROOT, 'seo', 'telegram.json'), 'last_cycle': (22, 17),
            'names': ('seo', 'сео')},
    # cycles at 08:41 and 16:41: after the last one the listener sleeps until the morning
    'sales': {'env': 'TELEGRAM_SALES_BOT_TOKEN', 'state': os.path.join(ROOT, 'sales', 'telegram.json'), 'last_cycle': (16, 41),
              'names': ('продажби', 'sales')},
    # one daily cycle at 11:13; the listener chains itself through the day and sleeps from 22:00
    'scout': {'env': 'TELEGRAM_SCOUT_BOT_TOKEN', 'state': os.path.join(ROOT, 'scout', 'telegram.json'), 'last_cycle': (22, 0),
              'names': ('разузнавач(?:ът|а)?', 'scout')},
}
DOCS = {'worker': 'CLAUDE.md', 'coder': 'coder/CODER.md', 'seo': 'seo/SEO.md', 'sales': 'sales/SALES.md', 'scout': 'scout/SCOUT.md'}
AS = 'worker'
if '--as' in sys.argv:
    i = sys.argv.index('--as')
    AS = sys.argv[i + 1]
    del sys.argv[i:i + 2]
FALLBACK = False  # manager without its own token: may only *send*, through the worker bot, with a 🧭 prefix
TZ = ZoneInfo('Europe/Sofia')
MORNING = (6, 30)     # no listener from the bot's last hourly cycle of the day until the morning
MAX_LISTEN = 6900     # a background command may run at most 2 h
# bare acknowledgements from bots are not tasks: they never wake an agent and get no reply
BOT_ACKS = {'', 'ок', 'ok', 'okay', 'окей', 'добре', 'благодаря', 'благодаря ти', 'мерси', 'thanks', 'thank you', 'супер', 'яко',
            'топ', 'браво', 'ясно', 'разбрах', 'прието', 'чудесно', 'страхотно', 'перфектно', 'отлично'}


def token(profile=None):
    global FALLBACK
    p = PROFILES[profile or AS]
    t = os.environ.get(p['env'], '').strip()
    if not t and (profile or AS) == 'manager' and os.environ.get('TELEGRAM_BOT_TOKEN', '').strip():
        FALLBACK = True
        t = os.environ['TELEGRAM_BOT_TOKEN'].strip()
        check_bot(t, 'worker', 'TELEGRAM_BOT_TOKEN')  # the fallback sends through the worker bot on purpose
        return t
    if not t:
        raise SystemExit(f"{p['env']} is not set: the owner adds it in the environment settings (Environment variables).")
    check_bot(t, profile or AS, p['env'])
    return t


class WrongBot(SystemExit):
    """The token belongs to another agent's bot. Never retried: reading with it would steal that agent's updates."""


EXPECTED_BOT = {'worker': ('plochko', '@dailyvideosswitfo_bot'), 'manager': ('_manager', '@managerswitfo_bot'),
                'coder': ('coder', '@itclaudeswitfo_bot'), 'seo': ('seo', None), 'sales': ('sales', None), 'scout': ('scout', None)}  # None: only from agents.json
ME_CACHE = '/tmp/daily-videos-telegram-getme.json'  # sha256(token)[:16] -> @username; never the token itself
_me = {}


def expected_bot(profile):
    key, default = EXPECTED_BOT[profile]
    try:
        a = json.load(open(os.path.join(ROOT, 'manager', 'agents.json'), encoding='utf-8')).get(key) or {}
    except (OSError, ValueError):
        a = {}
    want = a.get('telegram') or default
    if not want:
        raise WrongBot(f'manager/agents.json has no {key}.telegram (the bot\'s @username): the token cannot be checked, '
                       'so nothing was sent or read. The manager writes the bot name there.')
    return want.lower()


def bot_username(tok):
    """getMe for this token, cached in memory and in /tmp (a token's bot never changes). None if Telegram is unreachable."""
    import hashlib
    h = hashlib.sha256(tok.encode()).hexdigest()[:16]
    if h not in _me:
        try:
            _me.update(json.load(open(ME_CACHE, encoding='utf-8')))
        except (OSError, ValueError):
            pass
    if h in _me:
        return _me[h]
    r = subprocess.run(['curl', '-sS', '--max-time', '20', f'https://api.telegram.org/bot{tok}/getMe'], capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
    except json.JSONDecodeError:
        return None  # network hiccup: not verified now, the next call checks again
    if not d.get('ok'):
        raise SystemExit(f"Telegram getMe: {d.get('description', 'error')} (the token is not valid)")
    _me[h] = '@' + d['result']['username'].lower()
    try:
        cache = json.load(open(ME_CACHE, encoding='utf-8')) if os.path.exists(ME_CACHE) else {}
        cache[h] = _me[h]
        with open(ME_CACHE + '.tmp', 'w', encoding='utf-8') as f:
            json.dump(cache, f)
        os.replace(ME_CACHE + '.tmp', ME_CACHE)
    except (OSError, ValueError):
        pass
    return _me[h]


def check_bot(tok, profile, env):
    got, want = bot_username(tok), expected_bot(profile)
    if got and got != want:
        raise WrongBot(f'{env} is the token of {got}, not of {want}: nothing was sent or read. '
                       f'The owner puts the token of {want} (@BotFather) in {env} in the environment settings.')


def cfg():
    return json.load(open(CFG_PATH, encoding='utf-8')) if os.path.exists(CFG_PATH) else {'chat_id': None, 'allowed': [], 'offset': 0}


def state():
    p = PROFILES[AS]['state']
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {'offset': 0}


def save(c, path=None):
    path = path or CFG_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.tmp'  # write + rename: a listener stopped mid-write never leaves a broken file
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(c, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def api(method, params, profile=None):
    tok = token(profile)
    args = ['curl', '-sS', '--max-time', '60', '-X', 'POST', f'https://api.telegram.org/bot{tok}/{method}']
    for k, v in params.items():
        args += ['--data-urlencode', f'{k}={v if isinstance(v, str) else json.dumps(v)}']
    r = subprocess.run(args, capture_output=True, text=True)
    out = (r.stdout or r.stderr).replace(tok, '***')
    try:
        d = json.loads(out)
    except json.JSONDecodeError:
        raise SystemExit(f'Telegram {method}: {out[:300]}')
    if not d.get('ok'):
        raise SystemExit(f"Telegram {method}: {d.get('description', d)}")
    return d['result']


def who(u):
    return {'id': u.get('id'), 'username': ('@' + u['username'].lower()) if u.get('username') else None,
            'name': ' '.join(x for x in (u.get('first_name'), u.get('last_name')) if x)}


def setup():
    if AS != 'worker':
        return setup_bot()
    c = cfg()
    ups = api('getUpdates', {'timeout': 0, 'allowed_updates': ['message', 'my_chat_member']})
    chats, people = {}, {}
    for u in ups:
        m = u.get('message') or u.get('my_chat_member') or {}
        ch = m.get('chat') or {}
        if ch.get('type') in ('group', 'supergroup'):
            chats[ch['id']] = ch.get('title')
            frm = m.get('from') or {}
            if frm:
                people[frm['id']] = dict(who(frm), is_bot=bool(frm.get('is_bot')))
    c['bot_id'] = api('getMe', {})['id']
    if len(chats) == 1 and not c.get('chat_id'):
        c['chat_id'], c['chat_title'] = next(iter(chats.items()))
    save(c)
    print(json.dumps({'groups_seen': [{'id': k, 'title': v} for k, v in chats.items()], 'chat_id': c.get('chat_id'),
                      'people_seen': list(people.values()), 'allowed': c.get('allowed')}, ensure_ascii=False, indent=1))


def setup_bot():
    """Manager / coder: check our own bot (who it is, whether it sits in the group and reads all of it) and save its id.
    The shared group settings in data/telegram.json are the worker's; they are never changed from here."""
    c, s = cfg(), state()
    me = api('getMe', {})
    s['bot_id'], s['bot_username'] = me['id'], '@' + me['username'].lower()
    save(s, PROFILES[AS]['state'])
    out = {'bot': s['bot_username'], 'bot_id': me['id'], 'reads_all_group_messages': me.get('can_read_all_group_messages'),
           'chat_id': c.get('chat_id')}
    try:
        out['in_group'] = api('getChatMember', {'chat_id': str(c.get('chat_id')), 'user_id': str(me['id'])}).get('status')
    except SystemExit as e:
        out['in_group'] = f'no ({e}): the owner adds the bot to the group'
    print(json.dumps(out, ensure_ascii=False, indent=1))


def allow(x):
    c = cfg()
    x = x.strip().lower()
    x = x if x.lstrip('-').isdigit() else ('@' + x.lstrip('@'))
    if x not in c['allowed']:
        c['allowed'].append(x)
    save(c)
    print(json.dumps({'allowed': c['allowed']}, ensure_ascii=False))


def send(text, reply_to=None, quiet=False):
    c = cfg()
    if not c.get('chat_id'):
        raise SystemExit('No group yet: add the bot to the group, write a message there, then run `setup`.')
    token()
    if FALLBACK:
        text, reply_to = '🧭 Мениджър: ' + text, None  # sent by the worker bot; its message ids are not ours
    first = None
    for i in range(0, len(text), 3900):
        p = {'chat_id': str(c['chat_id']), 'text': text[i:i + 3900], 'disable_web_page_preview': 'true'}
        if reply_to and i == 0:
            p['reply_to_message_id'] = str(reply_to)
            p['allow_sending_without_reply'] = 'true'
        m = api('sendMessage', p)
        first = first or m.get('message_id')
    if not quiet:
        print('sent' + (' (чрез бота на Плочко — липсва TELEGRAM_MANAGER_BOT_TOKEN)' if FALLBACK else ''))
    return first


def send_photo(path, caption='', reply_to=None):
    """A picture to the group: sendPhoto, or sendDocument when Telegram refuses it as a photo (too big / too tall)."""
    c = cfg()
    if not c.get('chat_id'):
        raise SystemExit('No group yet: add the bot to the group, write a message there, then run `setup`.')
    if not os.path.isfile(path):
        raise SystemExit(f'No file {path}')
    tok = token()
    if FALLBACK:
        caption, reply_to = '🧭 Мениджър: ' + caption, None
    for method, field in (('sendPhoto', 'photo'), ('sendDocument', 'document')):
        if method == 'sendPhoto' and os.path.getsize(path) > 10 * 1024 * 1024:
            continue
        args = ['curl', '-sS', '--max-time', '120', '-X', 'POST', f'https://api.telegram.org/bot{tok}/{method}',
                '--form-string', f"chat_id={c['chat_id']}", '-F', f'{field}=@{path}']
        if caption:
            args += ['--form-string', f'caption={caption[:1000]}']
        if reply_to:
            args += ['--form-string', f'reply_to_message_id={reply_to}', '--form-string', 'allow_sending_without_reply=true']
        r = subprocess.run(args, capture_output=True, text=True)
        out = (r.stdout or r.stderr).replace(tok, '***')
        try:
            d = json.loads(out)
        except json.JSONDecodeError:
            d = {'ok': False, 'description': out[:300]}
        if d.get('ok'):
            print(f"sent ({'photo' if field == 'photo' else 'file'})")
            return d['result'].get('message_id')
        err = d.get('description', d)
    raise SystemExit(f'Telegram photo: {err}')


def check_reader():
    if AS == 'manager':
        token()
        if FALLBACK:
            raise SystemExit('TELEGRAM_MANAGER_BOT_TOKEN is not set: the manager cannot read the group (it must never read with the worker bot).')


def me_id(c, s):
    me = s.get('bot_id') or c.get('bot_id') if AS == 'worker' else s.get('bot_id')
    if not me:
        me_info = api('getMe', {})
        me, s['bot_id'], s['bot_username'] = me_info['id'], me_info['id'], '@' + me_info['username'].lower()
        if AS not in ('worker', 'manager'):  # remember it: the listener re-reads the state file and must still know our username
            save(s, PROFILES[AS]['state'])
    return me


def row(u, c, me):
    """One update -> a message row, or None if it is not a text message in our group from someone else."""
    m = u.get('message') or {}
    if not m or str((m.get('chat') or {}).get('id')) != str(c.get('chat_id')):
        return None
    frm = who(m.get('from') or {})
    if str(frm['id']) == str(me):
        return None
    text = m.get('text') or m.get('caption') or ''
    if not text.strip():
        return None
    rep = m.get('reply_to_message') or {}
    return {'message_id': m['message_id'], 'from': frm['username'] or frm['name'], 'from_id': frm['id'],
            'from_bot': bool((m.get('from') or {}).get('is_bot')), 'text': text, 'date': m.get('date'),
            'reply_to': rep.get('message_id'), 'reply_to_me': str((rep.get('from') or {}).get('id')) == str(me),
            'reply_to_from': who(rep['from'])['username'] if rep.get('from') else None,
            'task_ids': sorted(set(re.findall(r'\bM-\d{4}-\d{2,3}\b', text)))}


def updates():
    """New group messages since our last check (never our own). Advances and saves our offset."""
    check_reader()
    stop_listener()  # one reader per bot: the turn that reads the group takes over from its listener
    c, s = cfg(), state()
    me = me_id(c, s)
    ups = api('getUpdates', {'offset': str(int(s.get('offset') or 0) + 1), 'timeout': 0, 'allowed_updates': ['message']})
    capture_media(ups, c)
    out = []
    for u in ups:
        s['offset'] = max(int(s.get('offset') or 0), u['update_id'])
        r = row(u, c, me)
        if r:
            out.append(r)
    save(s, PROFILES[AS]['state'])
    if ups:  # confirm them on Telegram's side as well, so no other reader can get them again
        api('getUpdates', {'offset': str(s['offset'] + 1), 'timeout': 0, 'limit': 1, 'allowed_updates': ['message']})
    return out


def bare_ack(m):
    return m['from_bot'] and ' '.join(re.sub(r'[^\w\s]', ' ', m['text'].lower()).split()) in BOT_ACKS


def my_username(c, s=None):
    s = s if s is not None else state()
    return ((s.get('bot_username') or c.get('bot_username')) if AS == 'worker' else s.get('bot_username') or '').lower()


def for_worker(m, c, s=None):
    """Only the manager's messages meant for this agent (Плочко or the coder; the owner talks to the manager),
    never a bot's bare acknowledgement. A task header "→ @bot" decides alone: a task for another agent is not ours,
    even if it names us in the text."""
    if not ({m['from'], str(m['from_id'])} & set(c.get('allowed') or [])) or bare_ack(m):
        return False
    manager = c.get('manager_username')
    if manager and m['from'] != manager:
        return False  # owner -> manager only
    low, mine = m['text'].lower(), my_username(c, s)
    targets = [t.lower() for t in re.findall(r'→\s*(@\w+)', m['text'])]
    if targets:
        return bool(mine) and mine in targets
    if mine and re.search(rf'(?<![\w@]){re.escape(mine)}(?!\w)', low):
        return True
    if m['reply_to_me']:
        return True
    # The manager answering the owner is a conversation with the owner, not a task: only our @ (above) wakes us.
    owner = (c.get('owner') or '').lower()
    if owner and (m.get('reply_to_from') or '').lower() == owner:
        return False
    return any(named(n, low) for n in PROFILES[AS].get('names', ()))


def named(name, low):
    """`name` as a whole word: not inside another word or a hyphenated name (smartmenu-seo, seo-agent),
    and not the start of a name like "SEO - smartmenukj"."""
    return bool(re.search(rf'(?<![\w-]){name}(?![\w-])(?!\s+-\s*\w)', low))


def for_manager(m, c, s):
    """Wakes the manager: any message from the owner (the owner talks only to the manager).
    Agents' messages do not wake it: `inbox` reads them in the next cycle."""
    owner = (c.get('owner') or '').lower()
    return not m['from_bot'] and ((m['from'] or '').lower() == owner or str(m['from_id']) in (c.get('allowed') or []))


def tasks():
    """Worker / coder: only the manager's messages meant for us. The owner talks to the manager, who hands out the work,
    so owner messages are marked read here."""
    if AS == 'manager':
        raise SystemExit('The manager reads the group with `python3 src/manager.py inbox`.')
    c = cfg()
    for m in updates():
        if for_worker(m, c):
            print(json.dumps({k: m[k] for k in ('message_id', 'from', 'from_bot', 'text', 'date', 'reply_to', 'task_ids')}, ensure_ascii=False))
    if not is_night():  # `updates()` stopped the listener: remind the turn to start it again when it ends
        doc = DOCS[AS]
        print(f'(в края на хода пусни слушателя: `python3 src/telegram.py{flag()} listening` → при no `python3 src/telegram.py{flag()} wait` '
              f'във фонов режим; {doc}, „Слушател в реално време“)')


# ---------- media for Плочко (#плочко) ----------

MEDIA_LOG = os.path.join(ROOT, 'data', 'media.jsonl')
MEDIA_DIR = os.path.join(ROOT, 'out', 'media')
MEDIA_TAG = re.compile(r'#плочко\b', re.I)
MAX_BOT_FILE = 20 * 1024 * 1024  # getFile limit for bots


def media_rows():
    rows = []
    try:
        with open(MEDIA_LOG, encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))
    except FileNotFoundError:
        pass
    return rows


def media_of(m):
    """The file of a message: the largest photo size, a video, or a photo/video sent as a file (document)."""
    if m.get('photo'):
        p = max(m['photo'], key=lambda x: (x.get('file_size') or 0, x.get('width', 0) * x.get('height', 0)))
        return {'kind': 'photo', 'file_id': p['file_id'], 'file_unique_id': p['file_unique_id'], 'file_size': p.get('file_size'),
                'width': p.get('width'), 'height': p.get('height')}
    for key in ('video', 'animation', 'video_note'):
        if m.get(key):
            v = m[key]
            return {'kind': 'video', 'file_id': v['file_id'], 'file_unique_id': v['file_unique_id'], 'file_size': v.get('file_size'),
                    'width': v.get('width'), 'height': v.get('height'), 'duration': v.get('duration'), 'mime': v.get('mime_type')}
    d = m.get('document') or {}
    if d and (d.get('mime_type') or '').split('/')[0] in ('image', 'video'):
        return {'kind': d['mime_type'].split('/')[0].replace('image', 'photo'), 'file_id': d['file_id'], 'file_unique_id': d['file_unique_id'],
                'file_size': d.get('file_size'), 'mime': d.get('mime_type'), 'name': d.get('file_name')}
    return None


def capture_media(ups, c):
    """Worker only: keep the owner's #плочко photos/videos from these updates in data/media.jsonl (ids + text, no files)."""
    if AS != 'worker' or not ups:
        return 0
    owner = (c.get('owner') or '').lower()
    rows = media_rows()
    seen = {r['file_unique_id'] for r in rows}
    groups = {r['media_group_id']: r['text'] for r in rows if r.get('media_group_id')}
    msgs = [u.get('message') or {} for u in ups]
    for m in msgs:  # an album: the tag is on one item (its caption), the others carry no text
        if m.get('media_group_id') and MEDIA_TAG.search(m.get('caption') or ''):
            groups[m['media_group_id']] = m['caption']
    new = []
    for m in msgs:
        if not m or str((m.get('chat') or {}).get('id')) != str(c.get('chat_id')):
            continue
        if not owner or (who(m.get('from') or {})['username'] or '').lower() != owner:
            continue
        text = m.get('caption') or m.get('text') or ''
        if not MEDIA_TAG.search(text) and m.get('media_group_id') not in groups:
            continue
        f = media_of(m)
        if not f or f['file_unique_id'] in seen:
            continue
        seen.add(f['file_unique_id'])
        new.append({'message_id': m['message_id'], 'date': datetime.fromtimestamp(m.get('date', 0), TZ).isoformat(timespec='minutes'),
                    'text': (text if MEDIA_TAG.search(text) else groups.get(m.get('media_group_id'), '')).strip(),
                    **({'media_group_id': m['media_group_id']} if m.get('media_group_id') else {}), **{k: v for k, v in f.items() if v is not None}})
    if new:
        os.makedirs(os.path.dirname(MEDIA_LOG), exist_ok=True)
        with open(MEDIA_LOG, 'a', encoding='utf-8') as fh:
            for r in new:
                fh.write(json.dumps(r, ensure_ascii=False) + '\n')
    return len(new)


def media_file(r):
    """The downloaded copy of a media row in out/media/, if there is one."""
    try:
        for name in os.listdir(MEDIA_DIR):
            if name.split('.')[0] == r['file_unique_id']:
                return os.path.join(MEDIA_DIR, name)
    except FileNotFoundError:
        pass
    return None


def media(show_all=False):
    if AS != 'worker':
        raise SystemExit('media is for Плочко (the worker bot).')
    rows = media_rows()
    shown = 0
    for n, r in enumerate(rows, 1):
        path = media_file(r)
        if path and not show_all:
            continue
        shown += 1
        big = (r.get('file_size') or 0) > MAX_BOT_FILE
        print(json.dumps({'n': n, 'kind': r['kind'], 'file_id': r['file_id'], 'text': r['text'], 'date': r['date'],
                          'size_mb': round((r.get('file_size') or 0) / 1048576, 1), 'downloaded': os.path.relpath(path, ROOT) if path else None,
                          **({'too_big': 'над 20 MB: собственикът да я прати по-къса или като файл до 20 MB'} if big else {})}, ensure_ascii=False))
    if not shown:
        print('Няма нови снимки/видеа с #плочко.' if not show_all else 'Още няма снимки/видеа с #плочко.')


def media_get(which, dest_dir=None):
    if AS != 'worker':
        raise SystemExit('media is for Плочко (the worker bot).')
    rows = media_rows()
    if which == 'all':
        picked = [r for r in rows if not media_file(r)]
    elif re.fullmatch(r'\d+', which) and 1 <= int(which) <= len(rows):
        picked = [rows[int(which) - 1]]
    else:
        picked = [r for r in rows if r['file_id'] == which]
    if not picked:
        raise SystemExit(f'media get: no such item ({which}); see `python3 src/telegram.py media`.')
    out_dir = os.path.join(ROOT, dest_dir) if dest_dir and not os.path.isabs(dest_dir) else (dest_dir or MEDIA_DIR)
    os.makedirs(out_dir, exist_ok=True)
    for r in picked:
        if (r.get('file_size') or 0) > MAX_BOT_FILE:
            print(f"✗ {r['file_unique_id']}: {round(r['file_size'] / 1048576, 1)} MB — над 20 MB, ботът не може да го свали. "
                  'Помоли собственика да го прати по-късо или като файл до 20 MB.')
            continue
        try:
            info = api('getFile', {'file_id': r['file_id']})
        except SystemExit as e:
            print(f"✗ {r['file_unique_id']}: {e}" + (' — помоли собственика да го прати по-късо (до 20 MB).' if 'too big' in str(e) else ''))
            continue
        ext = os.path.splitext(info.get('file_path') or '')[1] or ('.jpg' if r['kind'] == 'photo' else '.mp4')
        dest = os.path.join(out_dir, r['file_unique_id'] + ext)
        tok = token()
        res = subprocess.run(['curl', '-sS', '--fail', '--max-time', '300', '-o', dest, f"https://api.telegram.org/file/bot{tok}/{info['file_path']}"],
                             capture_output=True, text=True)
        if res.returncode:
            if os.path.exists(dest):
                os.remove(dest)
            print(f"✗ {r['file_unique_id']}: download failed ({(res.stderr or '').replace(tok, '***').strip()[:200]})")
            continue
        print(f"✓ {os.path.relpath(dest, ROOT)} — {r['text'][:120]}")


# ---------- listener ----------

def now():
    return datetime.now(TZ)


def cutoff(t):
    """The bot's last hourly cycle today: once it starts, the listener sleeps until the morning."""
    h, mi = PROFILES[AS]['last_cycle']
    return t.replace(hour=h, minute=mi, second=0, microsecond=0)


def is_night(t=None):
    t = t or now()
    return t >= cutoff(t) - timedelta(minutes=3) or (t.hour, t.minute) < MORNING


def pidfile():
    return f'/tmp/daily-videos-telegram-listener-{AS}.pid'


def listener_pid():
    try:
        pid = int(open(pidfile()).read().split()[0])
        os.kill(pid, 0)
        if 'telegram.py' in open(f'/proc/{pid}/cmdline').read():
            return pid
    except (OSError, ValueError, IndexError):
        pass
    return None


def stop_listener():
    pid = listener_pid()
    if pid and pid != os.getpid():
        os.kill(pid, signal.SIGTERM)
        for _ in range(30):
            if not listener_pid():
                break
            time.sleep(0.1)


def flag():
    return '' if AS == 'worker' else f' --as {AS}'


def failfile():
    return f'/tmp/daily-videos-telegram-listener-{AS}.failed'


def listening():
    pid = listener_pid()
    try:
        check_reader()
        token()
        problem = None
    except SystemExit as e:
        problem = str(e)
    if not problem and os.path.exists(failfile()) and time.time() - os.path.getmtime(failfile()) < 15 * 60:
        problem = 'the listener failed a few minutes ago: ' + open(failfile(), encoding='utf-8').read()[-300:].strip()
    if pid:
        print(f'yes (pid {pid}, {open(pidfile()).read().split(maxsplit=1)[1].strip()})')
    elif problem:
        print(f'off: {problem} -> do not start it now; say it in your summary')
    elif is_night():
        print('night: do not start the listener now (the morning cycle starts it)')
    else:
        print(f'no: start it in the background: python3 src/telegram.py{flag()} wait')


class Stopped(BaseException):
    """Raised by SIGTERM in the listener (not a SystemExit, so the retry loop cannot swallow it)."""


def wait(seconds=MAX_LISTEN):
    """Listener for an agent's session: polls Telegram (long polling, no AI cost) and exits as soon as a message
    for this bot arrives, so the background command wakes the agent within seconds."""
    check_reader()
    if is_night():
        print('Нощ е: слушателят не тръгва. Сутрешният цикъл ще го пусне.')
        sys.exit(2)
    stop_listener()  # newest listener wins: never two readers
    t = now()
    end = min(time.time() + min(int(seconds), MAX_LISTEN), (cutoff(t) + timedelta(minutes=25)).timestamp())
    until = datetime.fromtimestamp(end, TZ).strftime('%H:%M')
    open(pidfile(), 'w').write(f'{os.getpid()} listening until {until}')

    def stopped(*_):
        raise Stopped()
    signal.signal(signal.SIGTERM, stopped)
    consume = AS != 'manager'  # worker/coder drop what is not for them anyway; the manager's `inbox` must still see everything
    code, pending = 2, False
    try:
        while time.time() < end:
            c, s = cfg(), state()
            me = me_id(c, s)
            try:
                ups = api('getUpdates', {'offset': str(int(s.get('offset') or 0) + 1), 'allowed_updates': ['message'],
                                         'timeout': '0' if pending else str(max(1, min(50, int(end - time.time()))))})
            except WrongBot:
                raise
            except SystemExit as e:  # network hiccup, or another reader for a moment: try again shortly
                sys.stderr.write(f'{e}\n')
                time.sleep(5)
                continue
            s = state()  # re-read: a turn may have advanced the offset meanwhile
            off = int(s.get('offset') or 0)
            fresh = [u for u in ups if u['update_id'] > off]
            capture_media(fresh, c)
            for u in fresh:
                m = row(u, c, me)
                if m and (for_manager(m, c, s) if AS == 'manager' else for_worker(m, c, s)):
                    if AS != 'manager':
                        print(f"НОВА ЗАДАЧА в Telegram от {m['from']}: {m['text'][:300]}\n"
                              f'→ изпълни `python3 src/telegram.py{flag()} tasks` и действай по правилата (Прието → изпълни → Готово); '
                              'в края на хода пусни слушателя пак.')
                    else:
                        print(f"НОВО СЪОБЩЕНИЕ от собственика в Telegram: {m['text'][:300]}\n"
                              '→ изпълни `python3 src/manager.py inbox` и стъпка 1 от „Цикъл на мениджъра“; в края на хода пусни слушателя пак.')
                    code = 0  # the offset stays before this message, so the turn reads it
                    return
                if consume:
                    off = u['update_id']  # not for us: mark read
            if consume and off > int(state().get('offset') or 0):
                s = state()
                s['offset'] = off
                save(s, PROFILES[AS]['state'])
            pending = bool(fresh) and not consume
            if pending:
                time.sleep(20)  # messages the manager must leave for `inbox`: look again in 20 s without taking them
        print(f'Слушането изтече ({until}) без нови съобщения. В края на хода: '
              f'`python3 src/telegram.py{flag()} listening` → при no пусни `wait` пак.')
    except Exception:
        import traceback
        err = traceback.format_exc()
        sys.stderr.write(err)
        open(failfile(), 'w', encoding='utf-8').write(err)  # `listening` then says "off" for 15 min: no restart loop
        code = 1
    except WrongBot as e:  # a SystemExit, so the retry loop must not swallow it
        sys.stderr.write(f'{e}\n')
        open(failfile(), 'w', encoding='utf-8').write(str(e))
        code = 1
    except Stopped:
        print(f'Слушателят спря: ходът чете Telegram сам. В края на хода го пусни пак, ако `python3 src/telegram.py{flag()} listening` каже no.')
        code = 3
    finally:
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        if listener_pid() == os.getpid():
            os.remove(pidfile())
        sys.stdout.flush()
        os._exit(code)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'tasks'
    if cmd == 'setup':
        setup()
    elif cmd == 'allow':
        allow(sys.argv[2])
    elif cmd == 'send':
        send(sys.argv[2])
    elif cmd == 'reply':
        send(sys.argv[3], reply_to=sys.argv[2])
    elif cmd == 'photo':
        send_photo(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else '', sys.argv[4] if len(sys.argv) > 4 else None)
    elif cmd == 'tasks':
        tasks()
    elif cmd == 'media':
        if len(sys.argv) > 2 and sys.argv[2] == 'get':
            media_get(sys.argv[3] if len(sys.argv) > 3 else 'all', sys.argv[4] if len(sys.argv) > 4 else None)
        else:
            media(show_all=len(sys.argv) > 2 and sys.argv[2] == 'all')
    elif cmd == 'listening':
        listening()
    elif cmd == 'wait':
        wait(int(sys.argv[2]) if len(sys.argv) > 2 else MAX_LISTEN)
    else:
        raise SystemExit(__doc__)
