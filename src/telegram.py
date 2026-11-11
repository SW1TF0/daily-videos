"""Telegram group "Claude cluster" = the command centre of the agents. Two bots share it:
the worker (Плочко, daily videos) and the manager (@managerswitfo_bot), who watches the agents and hands out tasks.

python3 src/telegram.py setup                    # find the group + people from recent messages -> data/telegram.json
python3 src/telegram.py allow <@username|id>     # who may give tasks (manager, owner)
python3 src/telegram.py send "<text>"            # post to the group
python3 src/telegram.py tasks                    # new messages addressed to us from allowed people (JSON lines); marks them read
python3 src/telegram.py reply <message_id> "<text>"   # answer a specific task message
python3 src/telegram.py listening                # yes | no | night | off  -> start `wait` (in the background) only on "no"
python3 src/telegram.py wait                     # listener: waits without AI cost, exits as soon as a message for us arrives
                                                 # exit 0 = new message for us, 2 = time is up, 3 = a turn reads Telegram itself

Add `--as manager` (e.g. `python3 src/telegram.py --as manager send "..."`) to act as the manager bot;
the manager reads the group with `python3 src/manager.py inbox`.

Tokens come from the environment (TELEGRAM_BOT_TOKEN for the worker, TELEGRAM_MANAGER_BOT_TOKEN for the manager,
set in the environment's settings) and are never printed or written to the repo.
In a basic group message ids are per bot: refer to tasks by their id (M-1111-01) in the text, never by another bot's message id.

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
    'worker': {'env': 'TELEGRAM_BOT_TOKEN', 'state': CFG_PATH, 'last_cycle': (23, 23)},
    'manager': {'env': 'TELEGRAM_MANAGER_BOT_TOKEN', 'state': os.path.join(ROOT, 'manager', 'telegram.json'), 'last_cycle': (22, 53)},
}
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


def for_worker(m, c):
    """Only the manager's messages meant for Плочко (the owner talks to the manager), never a bot's bare acknowledgement."""
    if not ({m['from'], str(m['from_id'])} & set(c.get('allowed') or [])) or bare_ack(m):
        return False
    manager = c.get('manager_username')
    if manager and m['from'] != manager:
        return False  # owner -> manager only
    low, mine = m['text'].lower(), (c.get('bot_username') or '').lower()
    return bool(m['reply_to_me'] or (mine and mine in low) or 'плочко' in low)


def for_manager(m, c, s):
    """Wakes the manager: any message from the owner (the owner talks only to the manager).
    Agents' messages do not wake it: `inbox` reads them in the next cycle."""
    owner = (c.get('owner') or '').lower()
    return not m['from_bot'] and ((m['from'] or '').lower() == owner or str(m['from_id']) in (c.get('allowed') or []))


def tasks():
    """Worker: only the manager's messages meant for us. The owner talks to the manager, who hands out the work,
    so owner messages are marked read here."""
    c = cfg()
    for m in updates():
        if for_worker(m, c):
            print(json.dumps({k: m[k] for k in ('message_id', 'from', 'from_bot', 'text', 'date', 'reply_to', 'task_ids')}, ensure_ascii=False))
    if not is_night():  # `updates()` stopped the listener: remind the turn to start it again when it ends
        print('(в края на хода пусни слушателя: `python3 src/telegram.py listening` → при no `python3 src/telegram.py wait` '
              'във фонов режим; CLAUDE.md, „Слушател в реално време“)')


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
    return ' --as manager' if AS == 'manager' else ''


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
    consume = AS == 'worker'  # the worker drops what is not for it anyway; the manager's `inbox` must still see everything
    code, pending = 2, False
    try:
        while time.time() < end:
            c, s = cfg(), state()
            me = me_id(c, s)
            try:
                ups = api('getUpdates', {'offset': str(int(s.get('offset') or 0) + 1), 'allowed_updates': ['message'],
                                         'timeout': '0' if pending else str(max(1, min(50, int(end - time.time()))))})
            except SystemExit as e:  # network hiccup, or another reader for a moment: try again shortly
                sys.stderr.write(f'{e}\n')
                time.sleep(5)
                continue
            s = state()  # re-read: a turn may have advanced the offset meanwhile
            off = int(s.get('offset') or 0)
            fresh = [u for u in ups if u['update_id'] > off]
            for u in fresh:
                m = row(u, c, me)
                if m and (for_worker(m, c) if AS == 'worker' else for_manager(m, c, s)):
                    if AS == 'worker':
                        print(f"НОВА ЗАДАЧА в Telegram от {m['from']}: {m['text'][:300]}\n"
                              '→ изпълни `python3 src/telegram.py tasks` и действай по правилата (Прието → изпълни → Готово); '
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
    elif cmd == 'tasks':
        tasks()
    elif cmd == 'listening':
        listening()
    elif cmd == 'wait':
        wait(int(sys.argv[2]) if len(sys.argv) > 2 else MAX_LISTEN)
    else:
        raise SystemExit(__doc__)
