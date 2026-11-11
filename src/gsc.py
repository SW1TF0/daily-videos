"""Google Search Console for the SEO agent, through a service account (stdlib + curl + openssl, no libraries).

python3 src/gsc.py sites                                     # properties the service account can see (and its permission)
python3 src/gsc.py sitemaps-submit <site> <sitemap-url>      # (re)submit a sitemap
python3 src/gsc.py sitemaps-list <site>                      # submitted sitemaps: last read, errors, URLs submitted/indexed
python3 src/gsc.py inspect <site> <url>                      # URL Inspection: indexed or not, and why
python3 src/gsc.py inspect-sitemap <site> [sitemap-url]      # inspect every URL of the sitemap (default <site>/sitemap.xml) + summary
python3 src/gsc.py performance <site> [days]                 # clicks / impressions / CTR / position by query and by page (default 28 days)

<site> is the property exactly as Search Console names it: "sc-domain:smartmenukj.com" (domain property) or
"https://www.smartmenukj.com/" (URL-prefix property). `sites` lists them.

The key: env GOOGLE_SA_JSON = the whole service-account JSON file (or a path to it), set by the owner in the
environment settings. It is never printed, logged or written to the repo; the private key exists on disk only for
the moment openssl signs the token (a 0600 temp file, deleted at once). The access token goes to curl through
stdin, never in the command line. Hosts: oauth2.googleapis.com, searchconsole.googleapis.com.
Google has no API for "Request indexing": a page gets indexed from the sitemap; `inspect` shows the state.
"""
import base64, datetime as dt, json, os, re, subprocess, sys, tempfile, time
from urllib.parse import quote

TOKEN_URL = 'https://oauth2.googleapis.com/token'
API = 'https://searchconsole.googleapis.com'
SCOPE = 'https://www.googleapis.com/auth/webmasters'  # read + submit sitemaps (".readonly" cannot submit)
RETRY = (429, 500, 502, 503, 504)
_token = {}


def fail(msg):
    raise SystemExit(f'gsc: {msg}')


def b64url(b):
    return base64.urlsafe_b64encode(b).rstrip(b'=').decode()


def service_account():
    raw = os.environ.get('GOOGLE_SA_JSON', '').strip()
    if not raw:
        fail('GOOGLE_SA_JSON is not set: the owner adds the service-account JSON in the environment settings '
             '(Environment variables), and adds the account as a user of the Search Console property.')
    if not raw.startswith('{') and os.path.isfile(raw):
        raw = open(raw, encoding='utf-8').read()
    try:
        sa = json.loads(raw)
    except json.JSONDecodeError:
        fail('GOOGLE_SA_JSON is not valid JSON (it must be the whole key file).')
    for k in ('client_email', 'private_key'):
        if not sa.get(k):
            fail(f'GOOGLE_SA_JSON has no "{k}" (it must be a service-account key file).')
    return sa


def sign(data, pem):
    """RS256 with openssl: the stdlib has no RSA."""
    fd, path = tempfile.mkstemp(prefix='gsc-', dir='/dev/shm' if os.path.isdir('/dev/shm') else None)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w') as f:
            f.write(pem)
        r = subprocess.run(['openssl', 'dgst', '-sha256', '-sign', path], input=data, capture_output=True)
    finally:
        os.unlink(path)
    if r.returncode or not r.stdout:
        fail('openssl could not sign with the private key in GOOGLE_SA_JSON (is it the right key file?)')
    return r.stdout


def curl(method, url, body=None, form=None, auth=None):
    """-> (status, parsed JSON or text). Secrets (bearer token, signed assertion) go to curl on stdin (-K -)."""
    conf = []
    if auth:
        conf.append(f'header = "Authorization: Bearer {auth}"')
    if form is not None:
        conf.append('data = "' + '&'.join(f'{k}={quote(str(v), safe="")}' for k, v in form.items()) + '"')
    cmd = ['curl', '-sS', '--connect-timeout', '20', '--max-time', '120', '-X', method, url, '-K', '-',
           '-w', '\n%{http_code}']
    if body is not None:
        cmd += ['-H', 'Content-Type: application/json', '--data-binary', json.dumps(body)]
    for attempt in range(3):
        r = subprocess.run(cmd, input='\n'.join(conf) + '\n', capture_output=True, text=True)
        if r.returncode:  # 6/7 = no connection, 28 = timeout, 56 = blocked by the proxy
            if attempt < 2 and r.returncode in (28, 35, 52, 56):
                time.sleep(2 * (attempt + 1))
                continue
            fail(f'{url.split("?")[0]}: curl exit {r.returncode} {r.stderr.strip()[:200]}'
                 + (' (is the host allowed in the environment network settings?)' if r.returncode in (6, 7, 56) else ''))
        text, _, code = r.stdout.rpartition('\n')
        status = int(code) if code.isdigit() else 0
        if status in RETRY and attempt < 2:
            time.sleep(2 * (attempt + 1))
            continue
        try:
            return status, json.loads(text) if text.strip() else {}
        except json.JSONDecodeError:
            return status, text
    return status, text


def token():
    if _token.get('exp', 0) > time.time() + 60:
        return _token['value']
    sa = service_account()
    now = int(time.time())
    head = b64url(json.dumps({'alg': 'RS256', 'typ': 'JWT'}).encode())
    claims = b64url(json.dumps({'iss': sa['client_email'], 'scope': SCOPE, 'aud': sa.get('token_uri') or TOKEN_URL,
                                'iat': now, 'exp': now + 3600}).encode())
    unsigned = f'{head}.{claims}'.encode()
    jwt = unsigned.decode() + '.' + b64url(sign(unsigned, sa['private_key']))
    status, d = curl('POST', TOKEN_URL, form={'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer', 'assertion': jwt})
    if status != 200 or not isinstance(d, dict) or not d.get('access_token'):
        err = d.get('error_description') or d.get('error') if isinstance(d, dict) else str(d)[:200]
        fail(f'no access token from Google ({status}): {err}')
    _token.update(value=d['access_token'], exp=now + int(d.get('expires_in', 3600)))
    return _token['value']


def api(method, path, body=None):
    status, d = curl(method, API + path, body=body, auth=token())
    if status >= 400 or status == 0:
        msg = d.get('error', {}).get('message') if isinstance(d, dict) and isinstance(d.get('error'), dict) else str(d)[:300]
        hint = (' — add the service account (its client_email) as a user of this property in Search Console'
                if status == 403 else ' — check the <site> name with `sites`' if status == 404 else '')
        fail(f'{method} {path.split("?")[0]} -> {status}: {msg}{hint}')
    return d if isinstance(d, dict) else {}


def site_path(site):
    if not (site.startswith('sc-domain:') or re.match(r'^https?://.+/$', site)):
        fail(f'<site> must be "sc-domain:example.com" or a URL-prefix property ending in "/": {site}')
    return quote(site, safe='')


def out(x):
    print(json.dumps(x, ensure_ascii=False, indent=1))


# ---------------------------------------------------------------- commands --

def sites():
    out([{'site': s.get('siteUrl'), 'permission': s.get('permissionLevel')} for s in api('GET', '/webmasters/v3/sites').get('siteEntry', [])])


def sitemaps_submit(site, sitemap):
    api('PUT', f'/webmasters/v3/sites/{site_path(site)}/sitemaps/{quote(sitemap, safe="")}')
    out({'submitted': sitemap, 'site': site})


def sitemaps_list(site):
    rows = []
    for s in api('GET', f'/webmasters/v3/sites/{site_path(site)}/sitemaps').get('sitemap', []):
        c = {x.get('type'): {'submitted': x.get('submitted'), 'indexed': x.get('indexed')} for x in s.get('contents', [])}
        rows.append({'sitemap': s.get('path'), 'last_submitted': s.get('lastSubmitted'), 'last_read': s.get('lastDownloaded'),
                     'pending': s.get('isPending'), 'errors': s.get('errors'), 'warnings': s.get('warnings'), 'contents': c})
    out(rows)


def inspect_one(site, url):
    d = api('POST', '/v1/urlInspection/index:inspect', {'inspectionUrl': url, 'siteUrl': site, 'languageCode': 'bg'})
    r = (d.get('inspectionResult') or {}).get('indexStatusResult') or {}
    return {'url': url, 'verdict': r.get('verdict'), 'coverage': r.get('coverageState'), 'indexing': r.get('indexingState'),
            'robots': r.get('robotsTxtState'), 'fetch': r.get('pageFetchState'), 'last_crawl': r.get('lastCrawlTime'),
            'google_canonical': r.get('googleCanonical'), 'user_canonical': r.get('userCanonical')}


def inspect(site, url):
    out(inspect_one(site, url))


def sitemap_urls(sitemap_url):
    r = subprocess.run(['curl', '-sS', '-L', '--connect-timeout', '20', '--max-time', '60', sitemap_url], capture_output=True, text=True)
    if r.returncode:
        fail(f'cannot download {sitemap_url}: curl exit {r.returncode} {r.stderr.strip()[:200]}')
    urls = re.findall(r'<loc>\s*([^<\s]+)\s*</loc>', r.stdout)
    if not urls:
        fail(f'no <loc> in {sitemap_url}')
    return urls


def inspect_sitemap(site, sitemap=None):
    if not sitemap:
        base = 'https://' + site.split(':', 1)[1] + '/' if site.startswith('sc-domain:') else site
        sitemap = base + 'sitemap.xml'
    rows, counts = [], {}
    for i, url in enumerate(sitemap_urls(sitemap)):
        if i:
            time.sleep(0.2)  # quota: 600 inspections a minute, 2000 a day per property
        r = inspect_one(site, url)
        rows.append(r)
        key = r['coverage'] or r['verdict'] or 'unknown'
        counts[key] = counts.get(key, 0) + 1
        print(json.dumps(r, ensure_ascii=False), flush=True)
    indexed = sum(1 for r in rows if r['verdict'] == 'PASS')
    out({'summary': {'sitemap': sitemap, 'urls': len(rows), 'indexed': indexed, 'not_indexed': len(rows) - indexed, 'by_state': counts}})


def performance(site, days=28):
    days = int(days)
    if not 1 <= days <= 480:
        fail('days must be 1–480')
    end = dt.date.today() - dt.timedelta(days=1)  # today has no data yet
    start = end - dt.timedelta(days=days - 1)
    res = {'site': site, 'from': start.isoformat(), 'to': end.isoformat()}
    total = api('POST', f'/webmasters/v3/sites/{site_path(site)}/searchAnalytics/query',
                {'startDate': start.isoformat(), 'endDate': end.isoformat(), 'dataState': 'all'}).get('rows') or [{}]
    t = total[0]
    res['total'] = {'clicks': t.get('clicks', 0), 'impressions': t.get('impressions', 0),
                    'ctr': round(t.get('ctr', 0) * 100, 1), 'position': round(t.get('position', 0), 1)}
    for dim in ('query', 'page'):
        rows = api('POST', f'/webmasters/v3/sites/{site_path(site)}/searchAnalytics/query',
                   {'startDate': start.isoformat(), 'endDate': end.isoformat(), 'dimensions': [dim], 'rowLimit': 25, 'dataState': 'all'}).get('rows', [])
        res[f'by_{dim}'] = [{dim: r['keys'][0], 'clicks': r.get('clicks', 0), 'impressions': r.get('impressions', 0),
                             'ctr': round(r.get('ctr', 0) * 100, 1), 'position': round(r.get('position', 0), 1)} for r in rows]
    out(res)


COMMANDS = {'sites': (sites, 0), 'sitemaps-submit': (sitemaps_submit, 2), 'sitemaps-list': (sitemaps_list, 1),
            'inspect': (inspect, 2), 'inspect-sitemap': (inspect_sitemap, 1), 'performance': (performance, 1)}

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] not in COMMANDS or len(a) - 1 < COMMANDS[a[0]][1]:
        raise SystemExit(__doc__)
    COMMANDS[a[0]][0](*a[1:])
