"""Publishing and analytics through Upload-Post (key injected by the environment proxy).

python3 src/social.py accounts                         # which networks are connected
python3 src/social.py publish out/<id>/meta.json "2026-11-11T19:30"   # schedule (Europe/Sofia), or "now"
python3 src/social.py metrics                          # snapshot stats of recent posts -> data/metrics.jsonl
python3 src/social.py audience                         # TikTok: followers online per hour (best time to post)
python3 src/social.py history                          # recent uploads with post URLs / errors
python3 src/social.py inbox [days]                     # unanswered comments on recent posts (JSON lines)
python3 src/social.py reply <platform> <post_id> <comment_id> "<text>"
python3 src/social.py skip <platform> <post_id> <comment_id> "<reason>"   # mark handled without replying
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


def call(method, path, params=None, form=None, headers=(), body=None):
    url = f'{API}{path}' + (('?' + urlencode(params)) if params else '')
    cmd = ['curl', '-sS', '-X', method, url, '-H', AUTH]
    if body is not None:
        cmd += ['-H', 'Content-Type: application/json', '-d', json.dumps(body, ensure_ascii=False)]
    for h in headers:
        cmd += ['-H', h]
    for k, v in (form or []):
        cmd += ['-F', f'{k}={v}']
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


def publish(meta_path, when):
    meta = json.load(open(meta_path, encoding='utf-8'))
    nets = list(accounts())
    if not nets:
        raise SystemExit('No networks connected in Upload-Post profile ' + PROFILE)
    hook = meta['hook'].replace('*', '').strip()
    tags = ' '.join(meta.get('hashtags') or [])
    caption = f"{meta.get('caption') or hook}\n\n{tags}".strip()
    form = [('user', PROFILE), ('video', '@' + meta['file']), ('title', caption[:2200]),
            ('youtube_title', (hook + ' #shorts')[:100]), ('description', caption[:4900]),
            ('external_id', meta['id']), ('async_upload', 'true')]
    form += [('platform[]', n) for n in nets]
    if when != 'now':
        form += [('scheduled_date', when), ('timezone', TZ)]
    res = call('POST', '/upload', form=form, headers=[f"Idempotency-Key: {meta['id']}"])
    ok = res.get('success', True) and not res.get('error')
    row = {'id': meta['id'], 'date': dt.date.today().isoformat(), 'scheduled_for': when, 'tz': TZ,
           'platforms': nets, 'request_id': res.get('request_id'), 'job_id': res.get('job_id'),
           'service': meta.get('service'), 'hook_style': meta.get('hook_style'), 'hook': hook,
           'duration': meta.get('duration'), 'ok': ok, 'response': {k: v for k, v in res.items() if k in ('message', 'error', 'warnings', 'status')}}
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
        publish(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 'now')
    elif cmd == 'metrics':
        metrics()
    elif cmd == 'audience':
        audience()
    elif cmd == 'inbox':
        inbox(int(sys.argv[2]) if len(sys.argv) > 2 else 14)
    elif cmd == 'reply':
        reply(*sys.argv[2:6])
    elif cmd == 'skip':
        skip(*sys.argv[2:6])
    elif cmd == 'history':
        for h in history():
            print(json.dumps({k: h.get(k) for k in ('platform', 'upload_timestamp', 'success', 'post_url', 'error_message', 'external_id')}, ensure_ascii=False))
