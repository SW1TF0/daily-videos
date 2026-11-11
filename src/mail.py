"""Read-only access to the service@smartmenukj.com mailbox (ABV) over IMAP, stdlib only.

python3 src/mail.py check                 # can we log in? (folder list, number of messages)
python3 src/mail.py list [days]           # messages of the last N days (default 3): uid, date, from, subject, seen-by-us — no body
python3 src/mail.py read <uid>            # one message as plain text (no attachments, only their names); marks it read in sales/mail.json

Login: env ABV_IMAP_USER and ABV_IMAP_PASSWORD (never printed); host env ABV_IMAP_HOST (default imap.abv.bg), port
ABV_IMAP_PORT (default 993, TLS). The mailbox is opened read-only (EXAMINE + BODY.PEEK), so nothing changes on the
server: no \\Seen flag, no deletes. What we have read is kept in sales/mail.json (only the uids).

Network: IMAP is not HTTPS. The cloud environments' proxy carries only HTTPS on port 443, so this does NOT connect
from a cloud session (checked 11.11.2026: CONNECT imap.abv.bg:993 is reset). It works where there is a direct
connection (the owner's computer, a session with Remote Control).
"""
import datetime as dt, email, email.header, email.utils, imaplib, json, os, re, socket, sys
from email.message import Message

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, 'sales', 'mail.json')
TIMEOUT = 30


def fail(msg):
    raise SystemExit(f'mail: {msg}')


def connect():
    user, pw = os.environ.get('ABV_IMAP_USER', '').strip(), os.environ.get('ABV_IMAP_PASSWORD', '')
    if not user or not pw:
        fail('ABV_IMAP_USER / ABV_IMAP_PASSWORD are not set: the owner adds them in the environment settings.')
    host, port = os.environ.get('ABV_IMAP_HOST', 'imap.abv.bg'), int(os.environ.get('ABV_IMAP_PORT', '993'))
    try:
        m = imaplib.IMAP4_SSL(host, port, timeout=TIMEOUT)
    except (OSError, socket.timeout) as e:
        fail(f'no connection to {host}:{port} ({type(e).__name__}). IMAP does not go through the HTTPS-only proxy of the '
             'cloud environments: run it where there is a direct connection, or forward the mail to Gmail.')
    try:
        m.login(user, pw)
    except imaplib.IMAP4.error:
        fail(f'login refused for {user} (wrong password, or IMAP access is off in the ABV settings)')
    return m


def text(h):
    """A decoded header (=?UTF-8?B?...?= etc.)."""
    if not h:
        return ''
    out = []
    for part, enc in email.header.decode_header(h):
        out.append(part.decode(enc or 'utf-8', 'replace') if isinstance(part, bytes) else part)
    return re.sub(r'\s+', ' ', ''.join(out)).strip()


def load_state():
    try:
        return json.load(open(STATE, encoding='utf-8'))
    except (OSError, ValueError):
        return {'read': []}


def save_state(s):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    tmp = STATE + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(s, f, indent=1)
    os.replace(tmp, STATE)


def ok(res, what):
    typ, data = res
    if typ != 'OK':
        fail(f'{what}: {data!r}'[:300])
    return data


def check():
    m = connect()
    try:
        folders = [re.sub(rb'.*"[./]" ', b'', f).decode('utf-8', 'replace').strip('"') for f in ok(m.list(), 'LIST') if f]
        n = int(ok(m.select('INBOX', readonly=True), 'EXAMINE INBOX')[0] or 0)
        print(json.dumps({'ok': True, 'inbox_messages': n, 'folders': folders}, ensure_ascii=False, indent=1))
    finally:
        m.logout()


def list_(days=3):
    since = (dt.date.today() - dt.timedelta(days=int(days))).strftime('%d-%b-%Y')
    read = set(load_state()['read'])
    m = connect()
    try:
        ok(m.select('INBOX', readonly=True), 'EXAMINE INBOX')
        uids = ok(m.uid('SEARCH', None, 'SINCE', since), 'SEARCH')[0].split()
        rows = []
        for uid in uids[-200:]:
            data = ok(m.uid('FETCH', uid, '(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])'), 'FETCH')
            raw = next((d[1] for d in data if isinstance(d, tuple)), b'')
            h = email.message_from_bytes(raw)
            rows.append({'uid': uid.decode(), 'date': text(h['Date']), 'from': text(h['From']), 'subject': text(h['Subject']),
                         'read_by_us': uid.decode() in read})
        for r in reversed(rows):
            print(json.dumps(r, ensure_ascii=False))
        print(json.dumps({'messages': len(rows), 'new_for_us': sum(1 for r in rows if not r['read_by_us']), 'since': since}))
    finally:
        m.logout()


def body_text(msg: Message):
    """The plain-text part (or HTML stripped to text); attachments only by name."""
    plain, html, files = [], [], []
    for part in msg.walk():
        if part.is_multipart():
            continue
        name = part.get_filename()
        if name or part.get_content_disposition() == 'attachment':
            files.append(text(name) or '(без име)')
            continue
        payload = part.get_payload(decode=True) or b''
        s = payload.decode(part.get_content_charset() or 'utf-8', 'replace')
        (plain if part.get_content_type() == 'text/plain' else html if part.get_content_type() == 'text/html' else []).append(s)
    if plain:
        body = '\n'.join(plain)
    else:
        body = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', '\n'.join(html), flags=re.S | re.I)
        body = re.sub(r'<br\s*/?>|</p>', '\n', body, flags=re.I)
        body = re.sub(r'<[^>]+>', '', body)
        body = re.sub(r'&nbsp;', ' ', body)
    return re.sub(r'\n{3,}', '\n\n', body).strip(), files


def read(uid):
    if not re.fullmatch(r'\d+', uid):
        fail('uid must be a number (from `list`)')
    m = connect()
    try:
        ok(m.select('INBOX', readonly=True), 'EXAMINE INBOX')
        data = ok(m.uid('FETCH', uid, '(BODY.PEEK[])'), 'FETCH')
        raw = next((d[1] for d in data if isinstance(d, tuple)), None)
        if not raw:
            fail(f'no message with uid {uid}')
        msg = email.message_from_bytes(raw)
        body, files = body_text(msg)
        print(json.dumps({'uid': uid, 'date': text(msg['Date']), 'from': text(msg['From']), 'reply_to': text(msg['Reply-To']),
                          'subject': text(msg['Subject']), 'attachments': files, 'text': body[:20000]}, ensure_ascii=False, indent=1))
    finally:
        m.logout()
    s = load_state()
    if uid not in s['read']:
        s['read'].append(uid)
        save_state(s)


if __name__ == '__main__':
    a = sys.argv[1:]
    cmd = a[0] if a else ''
    if cmd == 'check':
        check()
    elif cmd == 'list':
        list_(a[1] if len(a) > 1 else 3)
    elif cmd == 'read' and len(a) > 1:
        read(a[1])
    else:
        raise SystemExit(__doc__)
