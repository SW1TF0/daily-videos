"""Publishing and analytics through Upload-Post (key injected by the environment proxy).

python3 src/social.py accounts                         # which networks are connected
python3 src/social.py publish out/<id>/meta.json "2026-11-11T19:30" [tiktok,youtube]   # schedule (Europe/Sofia) or "now"; optional network subset
python3 src/social.py metrics                          # snapshot stats of recent posts -> data/metrics.jsonl
python3 src/social.py audience                         # TikTok: followers online per hour (best time to post)
python3 src/social.py history                          # recent uploads with post URLs / errors
python3 src/social.py post out/<id>/meta.json "2026-11-11T17:00" [instagram,tiktok]   # carousel/photo post (build_post.py)
python3 src/social.py followers                        # followers per network -> data/followers.jsonl (goal tracking)
python3 src/social.py inbox [days]                     # unanswered comments on recent posts (JSON lines)
python3 src/social.py reply <platform> <post_id> <comment_id> "<text>"
python3 src/social.py skip <platform> <post_id> <comment_id> "<reason>"   # mark handled without replying
python3 src/social.py dms [hours]                      # Instagram DM threads waiting for our answer (JSON lines)
python3 src/social.py dm <recipient_id> "<text>"        # send an Instagram DM (only within 24h of their last message)
"""
import datetime as dt, json, os, subprocess, sys
from urllib.parse import urlencode

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = 'https://api.upload-post.com/api'
AUTH = 'Authorization: Apikey proxy-injected'
PROFILE = os.environ.get('UPLOAD_POST_PROFILE', 'default')
TZ = 'Europe/Sofia'
NETWORKS = ['tiktok', 'instagram', 'facebook', 'youtube']
VIDEOS = os.path.join(ROOT, 'data', 'videos.jsonl')
METRICS = os.path.join(ROOT, 'data', 'metrics.jsonl')
COMMENTS = os.path.join(ROOT, 'data', 'comments.jsonl')
FOLLOWERS = os.path.join(ROOT, 'data', 'followers.jsonl')
DMS = os.path.join(ROOT, 'data', 'dms.jsonl')
ME = os.environ.get('IG_USERNAME', 'smartmenukj').lower()
GOAL = {'followers': 5000, 'start': '2026-11-10', 'deadline': '2026-12-10'}


def call(method, path, params=None, form=None, headers=(), body=None):
    url = f'{API}{path}' + (('?' + urlencode(params)) if params else '')
    cmd = ['curl', '-sS', '-X', method, url, '-H', AUTH]
    if body is not None:
        cmd += ['-H', 'Content-Type: application/json', '-d', json.dumps(body, ensure_ascii=False)]
    for h in headers:
        cmd += ['-H', h]
    for k, v in (form or []):
        # files go with -F name=@path; every text field with --form-string so ';', '@' or '<' in captions stay literal
        cmd += ['-F', f'{k}={v}'] if (k in ('video', 'photos[]') and str(v).startswith('@')) else ['--form-string', f'{k}={v}']
    out = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        raise SystemExit(f'Upload-Post {path}: {out.stdout[:400]} {out.stderr[:200]}')


def accounts():
    d = call('GET', '/uploadposts/users')
    for p in d.get('profiles', []):
        if p.get('username') == PROFILE:
            return {k: v for k, v in (p.get('social_accounts') or {}).items() if v and k in NETWORKS}
    return {}


def read_jsonl(path):
    if not os.path.exists(path):
        return []
    return [json.loads(l) for l in open(path, encoding='utf-8') if l.strip()]


def append_jsonl(path, row):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'a', encoding='utf-8') as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + '\n')


def publish(meta_path, when, only=None):
    meta = json.load(open(meta_path, encoding='utf-8'))
    nets = list(accounts())
    if only:  # e.g. add an already published video to networks connected later
        nets = [n for n in nets if n in only.split(',')]
    if not nets:
        raise SystemExit('No networks connected in Upload-Post profile ' + PROFILE)
    hook = meta['hook'].replace('*', '').strip()
    tags = ' '.join(meta.get('hashtags') or [])
    caption = f"{meta.get('caption') or hook}\n\n{tags}".strip()
    form = [('user', PROFILE), ('video', '@' + meta['file']), ('title', caption[:2200]),
            ('youtube_title', (hook + ' #shorts')[:100]), ('description', caption[:4900]),
            ('external_id', meta['id']), ('async_upload', 'true')]
    form += [('thumb_offset', '1000'), ('cover_timestamp', '1000')]  # cover = hook + Plochko at 1 s
    if when != 'now':
        form += [('scheduled_date', when), ('timezone', TZ)]

    def send(networks, key):
        return call('POST', '/upload', form=form + [('platform[]', n) for n in networks], headers=[f'Idempotency-Key: {key}'])

    key = meta['id'] + ('' if not only else '-' + '-'.join(sorted(nets)))  # new key, or Upload-Post returns the old job
    res = send(nets, key)
    ok = res.get('success', True) and not res.get('error')
    if not ok and 'tiktok' in nets and 'tiktok' in json.dumps(res).lower():
        # e.g. TikTok is not available on the Upload-Post Free plan: publish everywhere else
        nets = [n for n in nets if n != 'tiktok']
        res = dict(send(nets, meta['id'] + '-no-tiktok'), tiktok_skipped=str(res)[:300])
        ok = res.get('success', True) and not res.get('error')
    row = {'id': meta['id'], 'date': dt.date.today().isoformat(), 'scheduled_for': when, 'tz': TZ,
           'platforms': nets, 'request_id': res.get('request_id'), 'job_id': res.get('job_id'),
           'service': meta.get('service'), 'hook_style': meta.get('hook_style'), 'hook': hook,
           'duration': meta.get('duration'), 'ok': ok, 'response': {k: v for k, v in res.items() if k in ('message', 'error', 'warnings', 'status', 'tiktok_skipped')}}
    append_jsonl(VIDEOS, row)
    print(json.dumps(row, ensure_ascii=False, indent=1))
    if not ok:
        raise SystemExit(1)


def publish_post(meta_path, when, only=None):
    """Carousel / photo post: Instagram, TikTok (photo mode, auto music), Facebook — YouTube has no photo posts."""
    meta = json.load(open(meta_path, encoding='utf-8'))
    nets = [n for n in accounts() if n in ('instagram', 'tiktok', 'facebook')]
    if only:
        nets = [n for n in nets if n in only.split(',')]
    if not nets:
        raise SystemExit('No photo-capable network connected')
    hook = (meta.get('hook') or '').replace('*', '').strip()
    tags = ' '.join(meta.get('hashtags') or [])
    caption = f"{meta.get('caption') or hook}\n\n{tags}".strip()
    form = [('user', PROFILE), ('title', caption[:2200]), ('description', caption[:4900]),
            ('tiktok_title', hook[:90]), ('tiktok_description', caption[:4000]), ('auto_add_music', 'true'),
            ('photo_cover_index', '0'), ('external_id', meta['id']), ('async_upload', 'true')]
    form += [('photos[]', '@' + f) for f in meta['photos']]
    if when != 'now':
        form += [('scheduled_date', when), ('timezone', TZ)]
    key = meta['id'] + ('' if not only else '-' + '-'.join(sorted(nets)))
    res = call('POST', '/upload_photos', form=form + [('platform[]', n) for n in nets], headers=[f'Idempotency-Key: {key}'])
    ok = res.get('success', True) and not res.get('error')
    row = {'id': meta['id'], 'kind': 'carousel', 'date': dt.date.today().isoformat(), 'scheduled_for': when, 'tz': TZ,
           'platforms': nets, 'request_id': res.get('request_id'), 'job_id': res.get('job_id'), 'service': meta.get('service'),
           'format': meta.get('format'), 'hook': hook, 'slides': len(meta['photos']), 'ok': ok,
           'response': {k: v for k, v in res.items() if k in ('message', 'error', 'warnings', 'status')}}
    append_jsonl(VIDEOS, row)
    print(json.dumps(row, ensure_ascii=False, indent=1))
    if not ok:
        raise SystemExit(1)


def history(limit=20):
    return call('GET', '/uploadposts/history', {'limit': limit, 'profile_username': PROFILE}).get('history', [])


def metrics():
    """Snapshot per-post stats for posts of the last 14 days (by external_id = video id)."""
    now = dt.datetime.now(dt.timezone.utc)
    rows = history(100)
    seen = set()
    for h in rows:
        if not h.get('success') or not h.get('request_id'):
            continue
        ts = dt.datetime.fromisoformat(str(h['upload_timestamp']).replace('Z', '+00:00').replace(' ', 'T'))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=dt.timezone.utc)
        age_h = (now - ts).total_seconds() / 3600
        key = (h['request_id'], h['platform'])
        if age_h > 24 * 14 or key in seen:
            continue
        seen.add(key)
        d = call('GET', f"/uploadposts/post-analytics/{h['request_id']}", {'platform': h['platform']})
        pm = ((d.get('platforms') or {}).get(h['platform']) or {}).get('post_metrics') or {}
        row = {'at': now.isoformat(timespec='minutes'), 'video_id': h.get('external_id'), 'platform': h['platform'],
               'post_url': h.get('post_url'), 'posted_at': ts.isoformat(timespec='minutes'), 'hours_since_post': round(age_h, 1),
               **{k: pm.get(k) for k in ('views', 'likes', 'comments', 'shares', 'saves', 'favorites', 'reach', 'impressions',
                                          'avg_watch_time', 'average_view_duration', 'completion_rate') if k in pm}}
        append_jsonl(METRICS, row)
        print(json.dumps(row, ensure_ascii=False))


def _ts(v):
    try:
        v = str(v).replace('Z', '+00:00')
        if len(v) > 5 and v[-5] in '+-' and v[-3] != ':':
            v = v[:-2] + ':' + v[-2:]
        t = dt.datetime.fromisoformat(v)
        return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)
    except Exception:
        return None


def inbox(days=14):
    """Print comments on recent posts that nobody has handled yet, one JSON object per line."""
    handled = {(r['platform'], str(r['comment_id'])) for r in read_jsonl(COMMENTS)}
    accs = accounts()
    since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)
    for plat, acc in accs.items():
        me = (acc.get('username') or acc.get('display_name') or '').lower() if isinstance(acc, dict) else ''
        media = call('GET', '/uploadposts/media', {'platform': plat, 'user': PROFILE, 'limit': 15}).get('media') or []
        for m in media:
            t = _ts(m.get('timestamp') or m.get('created_at') or m.get('published_at') or '')
            if t and t < since:
                continue
            pid = str(m.get('id'))
            d = call('GET', '/uploadposts/comments', {'platform': plat, 'user': PROFILE, 'post_id': pid, 'limit': 50})
            for c in d.get('comments') or []:
                u = c.get('user') or c.get('from') or {}
                uname = (u.get('username') or u.get('name') or c.get('author') or '') if isinstance(u, dict) else str(u)
                if (plat, str(c.get('id'))) in handled or (me and uname.lower() == me):
                    continue
                print(json.dumps({'platform': plat, 'post_id': pid, 'post': (m.get('caption') or m.get('title') or '')[:100],
                                  'post_url': m.get('permalink') or m.get('url'), 'comment_id': c.get('id'), 'user': uname,
                                  'text': c.get('text') or c.get('message'), 'at': c.get('timestamp') or c.get('created_time')}, ensure_ascii=False))


def reply(platform, post_id, comment_id, text):
    body = {'platform': platform, 'user': PROFILE, 'message': text, 'comment_id': comment_id}
    if platform in ('tiktok', 'youtube'):
        body['post_id'] = post_id
    res = call('POST', '/uploadposts/comments/create', body=body)
    ok = bool(res.get('success'))
    append_jsonl(COMMENTS, {'at': dt.datetime.now(dt.timezone.utc).isoformat(timespec='minutes'), 'platform': platform,
                            'post_id': post_id, 'comment_id': comment_id, 'action': 'replied' if ok else 'reply_failed',
                            'reply': text, 'error': None if ok else str(res)[:300]})
    print(json.dumps(res, ensure_ascii=False)[:500])
    if not ok:
        raise SystemExit(1)


def skip(platform, post_id, comment_id, reason):
    append_jsonl(COMMENTS, {'at': dt.datetime.now(dt.timezone.utc).isoformat(timespec='minutes'), 'platform': platform,
                            'post_id': post_id, 'comment_id': comment_id, 'action': 'skipped', 'reason': reason})


def dms(hours=48):
    """Instagram conversations whose latest message is from the other person (needs our answer)."""
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)).strftime('%Y-%m-%dT%H:%M:%SZ')
    d = call('GET', '/uploadposts/dms/conversations', {'platform': 'instagram', 'user': PROFILE, 'since': since, 'limit': 50, 'messages_limit': 6})
    if not d.get('success', True):
        raise SystemExit(f"DMs: {d.get('error') or d}")
    for c in d.get('conversations') or []:
        msgs = sorted((c.get('messages') or {}).get('data') or [], key=lambda m: m.get('created_time') or '')
        if not msgs:
            continue
        last = msgs[-1]
        frm = (last.get('from') or {})
        if (frm.get('username') or '').lower() == ME:
            continue  # we already answered
        others = [p for p in (c.get('participants') or {}).get('data', []) if (p.get('username') or '').lower() != ME]
        who = others[0] if others else frm
        print(json.dumps({'conversation': c.get('id'), 'user': who.get('username'), 'recipient_id': who.get('id'),
                          'updated': c.get('updated_time'),
                          'thread': [{'from': 'ние' if (m.get('from') or {}).get('username', '').lower() == ME else 'клиент',
                                      'at': m.get('created_time'), 'text': m.get('message') or ('[' + ','.join(a.get('type', '?') for a in m.get('attachments') or []) + ']')}
                                     for m in msgs]}, ensure_ascii=False))


def dm(recipient_id, text):
    res = call('POST', '/uploadposts/dms/send', body={'platform': 'instagram', 'user': PROFILE, 'recipient_id': recipient_id, 'message': text})
    ok = bool(res.get('success'))
    append_jsonl(DMS, {'at': dt.datetime.now(dt.timezone.utc).isoformat(timespec='minutes'), 'recipient_id': recipient_id,
                       'text': text, 'ok': ok, 'error': None if ok else str(res)[:300]})
    print(json.dumps(res, ensure_ascii=False)[:400])
    if not ok:
        raise SystemExit(1)


def followers():
    """Record followers per connected network and print progress toward the goal."""
    nets = [n for n in accounts() if n != 'facebook']
    row = {'at': dt.datetime.now(dt.timezone.utc).isoformat(timespec='minutes')}
    if nets:
        d = call('GET', '/analytics/' + PROFILE, {'platforms': ','.join(nets)})
        for n in nets:
            v = (d.get(n) or {}).get('followers') if isinstance(d.get(n), dict) else None
            if v is not None:
                row[n] = int(v)
    total = sum(v for k, v in row.items() if k != 'at')
    row['total'] = total
    append_jsonl(FOLLOWERS, row)
    start, end = dt.date.fromisoformat(GOAL['start']), dt.date.fromisoformat(GOAL['deadline'])
    days_left = max(1, (end - dt.date.today()).days)
    need = max(0, GOAL['followers'] - total)
    print(json.dumps({**row, 'goal': GOAL['followers'], 'days_left': days_left, 'needed_per_day': round(need / days_left)}, ensure_ascii=False))


def audience():
    end = (dt.date.today() - dt.timedelta(days=1)).isoformat()
    start = (dt.date.today() - dt.timedelta(days=30)).isoformat()
    d = call('GET', '/uploadposts/audience', {'platform': 'tiktok', 'user': PROFILE, 'start_date': start, 'end_date': end})
    print(json.dumps({k: d.get(k) for k in ('range', 'activity_by_hour', 'timezone', 'error', 'message') if k in d}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'accounts'
    if cmd == 'accounts':
        print(json.dumps({k: (v.get('display_name') or v.get('username')) if isinstance(v, dict) else v for k, v in accounts().items()}, ensure_ascii=False))
    elif cmd == 'publish':
        publish(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 'now', sys.argv[4] if len(sys.argv) > 4 else None)
    elif cmd == 'metrics':
        metrics()
    elif cmd == 'audience':
        audience()
    elif cmd == 'dms':
        dms(int(sys.argv[2]) if len(sys.argv) > 2 else 48)
    elif cmd == 'dm':
        dm(sys.argv[2], sys.argv[3])
    elif cmd == 'post':
        publish_post(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 'now', sys.argv[4] if len(sys.argv) > 4 else None)
    elif cmd == 'followers':
        followers()
    elif cmd == 'inbox':
        inbox(int(sys.argv[2]) if len(sys.argv) > 2 else 14)
    elif cmd == 'reply':
        reply(*sys.argv[2:6])
    elif cmd == 'skip':
        skip(*sys.argv[2:6])
    elif cmd == 'history':
        for h in history():
            print(json.dumps({k: h.get(k) for k in ('platform', 'upload_timestamp', 'success', 'post_url', 'error_message', 'external_id')}, ensure_ascii=False))
