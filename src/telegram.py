"""Telegram group = the agent's command centre: reports go out, tasks from the manager come in.

python3 src/telegram.py setup                    # find the group + people from recent messages -> data/telegram.json
python3 src/telegram.py allow <@username|id>     # who may give tasks (manager, owner)
python3 src/telegram.py send "<text>"            # post to the group
python3 src/telegram.py tasks                    # new messages from allowed people (JSON lines); marks them as read
python3 src/telegram.py reply <message_id> "<text>"   # answer a specific task message

The bot token is read from the TELEGRAM_BOT_TOKEN environment variable (set in the environment's settings);
it is never printed. The bot must be an admin of the group (or have privacy mode off) to see all messages.
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG_PATH = os.path.join(ROOT, 'data', 'telegram.json')
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '').strip()


def cfg():
    return json.load(open(CFG_PATH, encoding='utf-8')) if os.path.exists(CFG_PATH) else {'chat_id': None, 'allowed': [], 'offset': 0}


def save(c):
    os.makedirs(os.path.dirname(CFG_PATH), exist_ok=True)
    json.dump(c, open(CFG_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def api(method, params):
    if not TOKEN:
        raise SystemExit('TELEGRAM_BOT_TOKEN is not set: add it in the environment settings (Environment variables).')
    args = ['curl', '-sS', '--max-time', '60', '-X', 'POST', f'https://api.telegram.org/bot{TOKEN}/{method}']
    for k, v in params.items():
        args += ['--data-urlencode', f'{k}={v if isinstance(v, str) else json.dumps(v)}']
    r = subprocess.run(args, capture_output=True, text=True)
    out = (r.stdout or r.stderr).replace(TOKEN, '***')
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
            if frm and not frm.get('is_bot'):
                people[frm['id']] = who(frm)
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


def send(text, reply_to=None):
    c = cfg()
    if not c.get('chat_id'):
        raise SystemExit('No group yet: add the bot to the group, write a message there, then run `setup`.')
    for i in range(0, len(text), 3900):
        p = {'chat_id': str(c['chat_id']), 'text': text[i:i + 3900], 'disable_web_page_preview': 'true'}
        if reply_to and i == 0:
            p['reply_to_message_id'] = str(reply_to)
        api('sendMessage', p)
    print('sent')


def tasks():
    """Messages in our group from allowed people since the last check; everything older is marked read."""
    c = cfg()
    ups = api('getUpdates', {'offset': str(int(c.get('offset') or 0) + 1), 'timeout': 0, 'allowed_updates': ['message']})
    allowed = set(c.get('allowed') or [])
    for u in ups:
        c['offset'] = max(int(c.get('offset') or 0), u['update_id'])
        m = u.get('message') or {}
        if not m or str((m.get('chat') or {}).get('id')) != str(c.get('chat_id')):
            continue
        frm = who(m.get('from') or {})
        if not ({frm['username'], str(frm['id'])} & allowed) or (m.get('from') or {}).get('is_bot'):
            continue
        text = m.get('text') or m.get('caption') or ''
        if text.strip():
            print(json.dumps({'message_id': m['message_id'], 'from': frm['username'] or frm['name'], 'text': text,
                              'date': m.get('date'), 'reply_to': (m.get('reply_to_message') or {}).get('message_id')}, ensure_ascii=False))
    save(c)


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
