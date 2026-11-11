"""Telegram group "Claude cluster" = the command centre of the agents. Two bots share it:
the worker (Плочко, daily videos) and the manager (@managerswitfo_bot), who watches the agents and hands out tasks.

python3 src/telegram.py setup                    # find the group + people from recent messages -> data/telegram.json
python3 src/telegram.py allow <@username|id>     # who may give tasks (manager, owner)
python3 src/telegram.py send "<text>"            # post to the group
python3 src/telegram.py tasks                    # new messages addressed to us from allowed people (JSON lines); marks them read
python3 src/telegram.py reply <message_id> "<text>"   # answer a specific task message

Add `--as manager` (e.g. `python3 src/telegram.py --as manager send "..."`) to act as the manager bot;
the manager reads the group with `python3 src/manager.py inbox`.

Tokens come from the environment (TELEGRAM_BOT_TOKEN for the worker, TELEGRAM_MANAGER_BOT_TOKEN for the manager,
set in the environment's settings) and are never printed or written to the repo.
In a basic group message ids are per bot: refer to tasks by their id (M-1111-01) in the text, never by another bot's message id.
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG_PATH = os.path.join(ROOT, 'data', 'telegram.json')  # shared: chat_id, allowed, owner + the worker's offset
PROFILES = {
    'worker': {'env': 'TELEGRAM_BOT_TOKEN', 'state': CFG_PATH},
    'manager': {'env': 'TELEGRAM_MANAGER_BOT_TOKEN', 'state': os.path.join(ROOT, 'manager', 'telegram.json')},
}
AS = 'worker'
if '--as' in sys.argv:
    i = sys.argv.index('--as')
    AS = sys.argv[i + 1]
    del sys.argv[i:i + 2]
FALLBACK = False  # manager without its own token: may only *send*, through the worker bot, with a 🧭 prefix


def token(profile=None):
    global FALLBACK
    p = PROFILES[profile or AS]
    t = os.environ.get(p['env'], '').strip()
    if not t and (profile or AS) == 'manager' and os.environ.get('TELEGRAM_BOT_TOKEN', '').strip():
        FALLBACK = True
        return os.environ['TELEGRAM_BOT_TOKEN'].strip()
    if not t:
        raise SystemExit(f"{p['env']} is not set: the owner adds it in the environment settings (Environment variables).")
    return t


def cfg():
    return json.load(open(CFG_PATH, encoding='utf-8')) if os.path.exists(CFG_PATH) else {'chat_id': None, 'allowed': [], 'offset': 0}


def state():
    p = PROFILES[AS]['state']
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {'offset': 0}


def save(c, path=None):
    path = path or CFG_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(c, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


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


def updates():
    """New group messages since our last check (never our own). Advances and saves our offset."""
    if AS == 'manager':
        token()
        if FALLBACK:
            raise SystemExit('TELEGRAM_MANAGER_BOT_TOKEN is not set: the manager cannot read the group (it must never read with the worker bot).')
    c, s = cfg(), state()
    me = s.get('bot_id') or c.get('bot_id') if AS == 'worker' else s.get('bot_id')
    if not me:
        me_info = api('getMe', {})
        me, s['bot_id'], s['bot_username'] = me_info['id'], me_info['id'], '@' + me_info['username'].lower()
    ups = api('getUpdates', {'offset': str(int(s.get('offset') or 0) + 1), 'timeout': 0, 'allowed_updates': ['message']})
    out = []
    for u in ups:
        s['offset'] = max(int(s.get('offset') or 0), u['update_id'])
        m = u.get('message') or {}
        if not m or str((m.get('chat') or {}).get('id')) != str(c.get('chat_id')):
            continue
        frm = who(m.get('from') or {})
        if str(frm['id']) == str(me):
            continue
        text = m.get('text') or m.get('caption') or ''
        if not text.strip():
            continue
        rep = m.get('reply_to_message') or {}
        out.append({'message_id': m['message_id'], 'from': frm['username'] or frm['name'], 'from_id': frm['id'],
                    'from_bot': bool((m.get('from') or {}).get('is_bot')), 'text': text, 'date': m.get('date'),
                    'reply_to': rep.get('message_id'), 'reply_to_me': str((rep.get('from') or {}).get('id')) == str(me),
                    'reply_to_from': who(rep['from'])['username'] if rep.get('from') else None,
                    'task_ids': sorted(set(re.findall(r'\bM-\d{4}-\d{2,3}\b', text)))})
    save(s, PROFILES[AS]['state'])
    return out


def tasks():
    """Worker: only the manager's messages meant for us. The owner talks to the manager, who hands out the work,
    so owner messages are marked read here."""
    c = cfg()
    allowed = set(c.get('allowed') or [])
    mine = (c.get('bot_username') or '').lower()
    manager = c.get('manager_username')
    for m in updates():
        if not ({m['from'], str(m['from_id'])} & allowed):
            continue
        if manager and m['from'] != manager:
            continue  # owner -> manager only
        low = m['text'].lower()
        addressed = m['reply_to_me'] or (mine and mine in low) or ('плочко' in low)
        if addressed:
            print(json.dumps({k: m[k] for k in ('message_id', 'from', 'from_bot', 'text', 'date', 'reply_to', 'task_ids')}, ensure_ascii=False))


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
    elif cmd == 'tasks':
        tasks()
    else:
        raise SystemExit(__doc__)
