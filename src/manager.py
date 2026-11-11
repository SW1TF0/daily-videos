"""The manager's tools: watch the agents, hand out tasks through the Telegram group, track them.

python3 src/manager.py inbox                       # new group messages (owner first); agents' "Прието/Готово M-…" update tasks
python3 src/manager.py status                      # health of every agent: today's output vs plan, failures, pace, open tasks, alerts
python3 src/manager.py task <agent> "<text>"       # new task M-MMDD-NN -> posted in the group to the agent's bot
python3 src/manager.py ask <agent> "<question>"    # question to an agent (same as a task, kind=question)
python3 src/manager.py tasks [all]                 # open tasks with age and status
python3 src/manager.py update <id> <status> ["note"]   # status: open|accepted|done|blocked|taken_over|cancelled
python3 src/manager.py takeover <id> "<note>"      # tell the group the manager does it itself (the agent must not)
python3 src/manager.py say "<text>"                # post to the group as the manager
python3 src/manager.py reply <message_id> "<text>" # answer a message (id as `inbox` printed it)

Agents are listed in manager/agents.json; the manager's own notes live in manager/agents/<agent>.md.
"""
import datetime as dt, json, os, subprocess, sys
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import telegram as tg  # noqa: E402

tg.AS = 'manager'  # every Telegram call here is made as the manager bot

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MDIR = os.path.join(ROOT, 'manager')
AGENTS = os.path.join(MDIR, 'agents.json')
TASKS = os.path.join(MDIR, 'tasks.json')
TZ = ZoneInfo('Europe/Sofia')
OPEN = ('open', 'accepted', 'blocked')


def now():
    return dt.datetime.now(TZ)


def load(path, default):
    return json.load(open(path, encoding='utf-8')) if os.path.exists(path) else default


def dump(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def agents():
    return load(AGENTS, {})


def agent_by_bot():
    return {a['telegram'].lower(): k for k, a in agents().items() if a.get('telegram')}


def read_jsonl(path):
    if not os.path.exists(path):
        return []
    rows = []
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return rows


def hours_since(iso):
    try:
        t = dt.datetime.fromisoformat(str(iso).replace('Z', '+00:00'))
        t = t if t.tzinfo else t.replace(tzinfo=TZ)
        return round((now() - t).total_seconds() / 3600, 1)
    except Exception:
        return None


# ---------- tasks ----------

def new_task(agent, text, kind='task'):
    ag = agents().get(agent)
    if not ag:
        raise SystemExit(f'Unknown agent {agent!r}; known: {", ".join(agents())}')
    db = load(TASKS, {'seq': {}, 'tasks': []})
    day = now().strftime('%m%d')
    n = db['seq'].get(day, 0) + 1
    db['seq'] = {day: n}
    tid = f'M-{day}-{n:02d}'
    head = '❓ Въпрос' if kind == 'question' else '📋 Задача'
    msg = (f"{head} {tid} → {ag['telegram']}\n{text}\n\n"
           f"Отговори с „Прието ✅ {tid}“, а когато е готово — „Готово ✅ {tid} — …“ (с линкове)." if kind == 'task' else
           f"{head} {tid} → {ag['telegram']}\n{text}\n\nОтговори с „Готово ✅ {tid} — …“.")
    mid = tg.send(msg, quiet=True)
    db['tasks'].append({'id': tid, 'agent': agent, 'kind': kind, 'text': text, 'status': 'open', 'created': now().isoformat(timespec='minutes'),
                        'updated': now().isoformat(timespec='minutes'), 'tg_message_id': mid, 'via': 'telegram-fallback' if tg.FALLBACK else 'telegram',
                        'history': []})
    dump(TASKS, db)
    out = {'id': tid, 'agent': agent, 'posted': True}
    if tg.FALLBACK:
        out['warning'] = ('Posted through the worker bot (no TELEGRAM_MANAGER_BOT_TOKEN): the agent ignores its own bot, '
                          f"so also wake it: fire_trigger {ag.get('triggers', {}).get('community')} with the task text and id.")
    print(json.dumps(out, ensure_ascii=False))
    return tid


def set_status(tid, status, note='', quiet=False):
    db = load(TASKS, {'seq': {}, 'tasks': []})
    for t in db['tasks']:
        if t['id'] == tid:
            if t['status'] != status or note:
                t['history'].append({'at': now().isoformat(timespec='minutes'), 'from': t['status'], 'to': status, 'note': note[:400]})
            t['status'], t['updated'] = status, now().isoformat(timespec='minutes')
            if note:
                t['last_note'] = note[:400]
            dump(TASKS, db)
            if not quiet:
                print(json.dumps({'id': tid, 'status': status}, ensure_ascii=False))
            return t
    if not quiet:
        raise SystemExit(f'No task {tid}')


def list_tasks(show_all=False):
    for t in load(TASKS, {'tasks': []})['tasks']:
        if show_all or t['status'] in OPEN:
            print(json.dumps({k: t.get(k) for k in ('id', 'agent', 'kind', 'status', 'text', 'last_note')} |
                             {'age_h': hours_since(t['created']), 'since_update_h': hours_since(t['updated'])}, ensure_ascii=False))


# ---------- inbox ----------

def inbox():
    """Owner messages and agents' messages since the last check. Task replies from agents update task status."""
    c = tg.cfg()
    owner = (c.get('owner') or '').lower()
    bots = agent_by_bot()
    me = (tg.state().get('bot_username') or '@managerswitfo_bot').lower()
    rows = []
    for m in tg.updates():
        low = m['text'].lower()
        frm = (m['from'] or '').lower()
        if frm in bots:
            kind = 'agent'
            for tid in m['task_ids']:
                st = ('done' if 'готово' in low else 'blocked' if any(w in low for w in ('не мога', 'блокира', 'провал', 'грешка', 'не успях'))
                      else 'accepted' if 'прието' in low else None)
                if st:
                    set_status(tid, st, m['text'], quiet=True)
            m['agent'] = bots[frm]
        elif frm == owner or str(m['from_id']) in (c.get('allowed') or []):
            kind = 'owner'
            to_agent = any(b in low for b in bots) or 'плочко' in low or (m.get('reply_to_from') or '').lower() in bots
            m['for_me'] = bool(m['reply_to_me'] or me in low or 'мениджър' in low or not to_agent)
        else:
            kind = 'other'
        m['kind'] = kind
        rows.append(m)
    rows.sort(key=lambda r: (r['kind'] != 'owner', r['date']))
    for r in rows:
        print(json.dumps({k: r.get(k) for k in ('kind', 'for_me', 'agent', 'message_id', 'from', 'text', 'reply_to_me', 'task_ids', 'date') if r.get(k) is not None},
                         ensure_ascii=False))
    if not rows:
        print(json.dumps({'new_messages': 0}))


# ---------- status ----------

def git_last(path):
    r = subprocess.run(['git', '-C', ROOT, 'log', '-1', '--format=%cI|%s', '--', path], capture_output=True, text=True)
    if not r.stdout.strip():
        return None
    at, subj = r.stdout.strip().split('|', 1)
    return {'at': at, 'hours_ago': hours_since(at), 'subject': subj[:100]}


def status_daily_videos(key, ag):
    """Health of the daily-videos agent (Плочко), from the repo data and Upload-Post."""
    t = ag.get('targets', {})
    today = now().date().isoformat()
    latest = {v.get('id'): v for v in read_jsonl(os.path.join(ROOT, 'data', 'videos.jsonl'))}  # re-published ids: the last row wins
    vids = sorted((v for v in latest.values() if str(v.get('scheduled_for', v.get('date', ''))).startswith(today)), key=lambda v: v.get('scheduled_for', ''))
    n_car = sum(1 for v in vids if v.get('kind') == 'carousel')
    n_vid = len(vids) - n_car
    failed_sched = [v['id'] for v in vids if v.get('ok') is False]
    fol = read_jsonl(os.path.join(ROOT, 'data', 'followers.jsonl'))
    last = fol[-1] if fol else {}
    start = dt.date.fromisoformat(t.get('goal_start', '2026-11-10'))
    end = dt.date.fromisoformat(t.get('deadline', '2026-12-10'))
    s0, goal = t.get('goal_start_followers', 23), t.get('followers_goal', 5000)
    days = (now().date() - start).days
    expected = round(s0 + (goal - s0) * min(1, days / max(1, (end - start).days)))
    day_ago = [r for r in fol if (hours_since(r['at']) or 0) >= 24]
    gain24 = (last.get('total', 0) - day_ago[-1]['total']) if day_ago and last else None
    out = {'agent': key, 'name': ag.get('name'), 'today': today,
           'scheduled_today': {'videos': n_vid, 'carousels': n_car, 'plan': f"{t.get('videos_per_day', 5)}+{t.get('carousels_per_day', 3)}",
                               'items': [f"{v.get('scheduled_for', '')[-5:]} {v.get('kind', 'video')} {v['id']}: {v.get('hook', '')}" for v in vids],
                               'failed_to_schedule': failed_sched},
           'followers': {'total': last.get('total'), 'by_network': {k: v for k, v in last.items() if k not in ('at', 'total')},
                         'snapshot_hours_ago': hours_since(last.get('at')), 'expected_today_on_pace': expected,
                         'behind_by': (expected - last['total']) if last else None, 'gain_24h': gain24,
                         'needed_per_day': round((goal - last.get('total', 0)) / max(1, (end - now().date()).days))},
           'last_commit': {'data': git_last('data'), 'playbook': git_last('playbook.md'), 'scripts': git_last('scripts')}}
    # The manager has no Upload-Post access of its own (owner's rule: bots talk, they don't share keys).
    # Upload results come from the worker's data in the repo and its reports; a live check only if a key happens to be there.
    try:
        if not os.environ.get('MANAGER_UPLOAD_POST'):
            raise LookupError('no Upload-Post access: ask the worker (ask plochko) for failed uploads')
        sys.path.insert(0, os.path.join(ROOT, 'src'))
        import social
        hist = social.history(50)
        recent = [h for h in hist if (hours_since(h.get('upload_timestamp')) or 99) <= 24]
        out['uploads_24h'] = {'ok': sum(1 for h in recent if h.get('success')),
                              'failed': [{'id': h.get('external_id'), 'platform': h.get('platform'), 'error': (h.get('error_message') or '')[:200],
                                          'stage': h.get('failure_stage')} for h in recent if not h.get('success')]}
    except BaseException as e:  # social.py raises SystemExit on API errors
        out['uploads_24h'] = {'error': str(e)[:200]}
    alerts = []
    h = now().hour
    if h >= 9 and n_vid < t.get('videos_per_day', 5):
        alerts.append(f"Днес са насрочени {n_vid} видеа от {t.get('videos_per_day', 5)}")
    if h >= 9 and n_car < t.get('carousels_per_day', 3):
        alerts.append(f"Днес са насрочени {n_car} карусела от {t.get('carousels_per_day', 3)}")
    if failed_sched:
        alerts.append(f"Неуспешно насрочени: {', '.join(failed_sched)}")
    if out['uploads_24h'].get('failed'):
        alerts.append(f"Провалени качвания за 24 ч.: {len(out['uploads_24h']['failed'])}")
    if out['uploads_24h'].get('error') and 'no Upload-Post access' not in out['uploads_24h']['error']:
        alerts.append('Upload-Post не отговаря: ' + out['uploads_24h']['error'][:80])
    snap = out['followers']['snapshot_hours_ago']
    if 9 <= h <= 23 and (snap is None or snap > 3):
        alerts.append(f"Няма нова снимка на последователите от {snap} ч. (цикълът „общност“ работи ли?)")
    if out['followers']['behind_by'] and out['followers']['behind_by'] > 0:
        alerts.append(f"Изоставане от целта: {out['followers']['behind_by']} последователи (днес трябва ~{expected})")
    out['alerts'] = alerts
    return out


CHECKS = {'daily-videos': status_daily_videos}


def status():
    res = {'now': now().isoformat(timespec='minutes'), 'agents': [], 'open_tasks': []}
    for key, ag in agents().items():
        fn = CHECKS.get(ag.get('check'))
        res['agents'].append(fn(key, ag) if fn else {'agent': key, 'name': ag.get('name'),
                                                     'note': 'no automatic check: watch it via list_triggers / list_events'})
    for t in load(TASKS, {'tasks': []})['tasks']:
        if t['status'] in OPEN:
            age, upd = hours_since(t['created']), hours_since(t['updated'])
            flag = ('без отговор' if t['status'] == 'open' and (age or 0) >= 2 else
                    'бави се' if t['status'] == 'accepted' and (upd or 0) >= 12 else
                    'блокирана' if t['status'] == 'blocked' else None)
            res['open_tasks'].append({'id': t['id'], 'agent': t['agent'], 'status': t['status'], 'text': t['text'][:160], 'age_h': age, 'flag': flag})
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    a = sys.argv[1:]
    cmd = a[0] if a else 'status'
    if cmd == 'inbox':
        inbox()
    elif cmd == 'status':
        status()
    elif cmd == 'task':
        new_task(a[1], a[2])
    elif cmd == 'ask':
        new_task(a[1], a[2], kind='question')
    elif cmd == 'tasks':
        list_tasks(len(a) > 1 and a[1] == 'all')
    elif cmd == 'update':
        set_status(a[1], a[2], a[3] if len(a) > 3 else '')
    elif cmd == 'takeover':
        t = set_status(a[1], 'taken_over', a[2] if len(a) > 2 else '', quiet=True)
        if not t:
            raise SystemExit(f'No task {a[1]}')
        tg.send(f"🛠 {a[1]}: поемам го аз — {agents()[t['agent']]['telegram']}, не го прави. {a[2] if len(a) > 2 else ''}".strip(), quiet=True)
        print(json.dumps({'id': a[1], 'status': 'taken_over'}))
    elif cmd == 'say':
        tg.send(a[1])
    elif cmd == 'reply':
        tg.send(a[2], reply_to=a[1])
    else:
        raise SystemExit(__doc__)
