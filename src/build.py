"""Build one vertical video from a script JSON.

python3 src/build.py scripts/<name>.json            -> out/<id>/<id>.mp4
python3 src/build.py scripts/<name>.json --stills   -> only preview stills (no full render)
"""
import hashlib, json, os, re, subprocess, sys, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src')
FPS = 30
LEAD = 0.45        # seconds of hook slam before the voice starts
END_DUR = 2.4      # end card length
VOICES = {  # native Bulgarian voices from the ElevenLabs library (added to the account)
    'mimi': 'CBDgRB8OyxYGowoi5iXR', 'nadya': 'mW3jGQPMrIgiOavQfIhc', 'elena': 'fSxb5mPM1l5zTVVtM3Vb',
    'nikolay': 'jFUMfgSnXMVNWDwPdkDf', 'georgi': '31jwlwrRwpOA5yGuVAby',
    'boris': 'UcGGwCMBEQAIYpXt4nTS', 'peter': '406EiNlYvqFqcz3vsnOm', 'georgi_ads': 'Ywe24jn5elUzaO9vm6vG',
    'kosta': 'gdk0ZsvfAOobfbTtnx6p', 'yordan': 'vZifugoCmJjNgn0bBdKH',
}
VOICE = {'voice': 'nikolay', 'model_id': 'eleven_v4', 'pitch': 1.0, 'settings': {'stability': 0.5}}
# how brand words are spoken (captions keep the written form)
PRON = {'SmartMenuKJ': 'Смарт Меню Кей Джей', '4G': 'фор джи', 'QR': 'кю ар', 'IP': 'ай пи'}
VOWEL = {**{c: 'a' for c in 'ая'}, **{c: 'e' for c in 'еий'}, **{c: 'o' for c in 'оую'}}


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit(f'command failed: {cmd[0]}')
    return r.stdout


def tts(text, cache_dir, voice):
    os.makedirs(cache_dir, exist_ok=True)
    vid = VOICES.get(voice['voice'], voice['voice'])
    body = {'text': text, 'model_id': voice['model_id'], 'language_code': 'bg', 'voice_settings': voice['settings']}
    key = hashlib.sha1(json.dumps([vid, body], ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:16]
    path = os.path.join(cache_dir, key + '.json')
    if not os.path.exists(path):
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{vid}/with-timestamps?output_format=mp3_44100_128"
        run(['curl', '-sS', '--retry', '3', '--retry-all-errors', '--retry-delay', '5', '--max-time', '180', '--fail-with-body', '-X', 'POST', url, '-H', 'xi-api-key: proxy-injected',
             '-H', 'Content-Type: application/json', '-d', json.dumps(body, ensure_ascii=False), '-o', path])
    d = json.load(open(path))
    if 'audio_base64' not in d:
        os.remove(path)
        raise SystemExit(f'TTS failed: {str(d)[:400]}')
    return d


def pexels_photo(query, orientation, avoid):
    """Search Pexels (real stock photos, free for commercial use) and download one image."""
    cache = os.path.join(ROOT, 'cache', 'photos')
    os.makedirs(cache, exist_ok=True)
    from urllib.parse import quote
    url = f'https://api.pexels.com/v1/search?query={quote(query)}&orientation={orientation}&size=large&per_page=20'
    res = json.loads(run(['curl', '-sS', '--fail-with-body', url, '-H', 'Authorization: proxy-injected']))
    photos = [ph for ph in res.get('photos', []) if str(ph['id']) not in avoid] or res.get('photos', [])
    if not photos:
        raise SystemExit(f'no Pexels photo for {query!r}')
    ph = photos[int(hashlib.sha1(query.encode()).hexdigest(), 16) % min(5, len(photos))]
    path = os.path.join(cache, f"pexels-{ph['id']}.jpg")
    if not os.path.exists(path):
        src = ph['src']['portrait'] if orientation == 'portrait' else ph['src']['large2x']
        run(['curl', '-sS', '-L', '--fail', src, '-o', path])
    return {'src': 'file://' + path, 'id': str(ph['id']), 'credit': ph.get('photographer', '')}


def resolve_photos(sc):
    """Turn photo queries in the script into local files. Returns the list of used Pexels ids."""
    used_file = os.path.join(ROOT, 'data', 'used_photos.txt')
    avoid = set(open(used_file).read().split()) if os.path.exists(used_file) else set()
    used = []

    def one(spec, orientation):
        if spec.get('src'):
            src = spec['src']
            return src if src.startswith(('file://', 'http')) else 'file://' + os.path.join(ROOT, src)
        r = pexels_photo(spec['query'], orientation, avoid)
        used.append(r['id'])
        avoid.add(r['id'])
        return r['src']

    def safe(spec, orientation):
        try:
            return one(spec, orientation)
        except (SystemExit, Exception) as e:  # no key / no result: the video still ships without that photo
            sys.stderr.write(f'photo skipped ({spec.get("query") or spec.get("src")}): {e}\n')
            return None

    if sc.get('hook_photo'):
        sc['_hook_photo'] = safe(sc['hook_photo'], 'portrait')
    for seg in sc['segments']:
        c = seg.get('card')
        if c and c.get('type') == 'photo':
            c['src'] = safe(c, 'landscape')
            if not c['src']:
                seg['card'] = {'type': 'title', 'icon': c.get('icon', '✨'), 'title': c.get('title', ''), 'sub': c.get('sub')}
    if used:
        os.makedirs(os.path.dirname(used_file), exist_ok=True)
        with open(used_file, 'a') as fh:
            fh.write('\n'.join(used) + '\n')
    return used


def tokenize(segments):
    """Split each segment's text into words; *word* marks emphasis."""
    full, words, seg_spans = '', [], []
    for si, seg in enumerate(segments):
        if full:
            full += ' '
        s0 = len(full)
        for tok in seg['say'].split():
            em = '*' in tok
            clean = tok.replace('*', '')
            if not clean:
                continue
            m = re.match(r'^([^\w]*)(.*?)([^\w]*)$', clean)
            spoken = m.group(1) + PRON.get(m.group(2), m.group(2)) + m.group(3)
            if len(full) > s0:
                full += ' '
            words.append({'w': clean, 'c0': len(full), 'c1': len(full) + len(spoken) - 1, 'seg': si, 'em': em})
            full += spoken
        seg_spans.append((s0, len(full) - 1))
    return full, words, seg_spans


def envelope(wav_path, n_frames):
    with wave.open(wav_path) as w:
        sr, ch = w.getframerate(), w.getnchannels()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').astype(np.float64)
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    hop = sr / FPS
    rms = np.zeros(n_frames)
    for i in range(n_frames):
        a, b = int(i * hop - hop / 2), int(i * hop + hop)
        seg = x[max(0, a):max(0, b)]
        rms[i] = np.sqrt(np.mean(seg ** 2)) if len(seg) else 0
    ref = np.percentile(rms[rms > 0], 92) if np.any(rms > 0) else 1
    e = np.clip(rms / ref, 0, 1.2)
    out = np.zeros_like(e)
    for i in range(len(e)):
        prev = out[i - 1] if i else 0
        k = 0.65 if e[i] > prev else 0.35
        out[i] = prev + (e[i] - prev) * k
    out[out < 0.12] = 0
    # small open/close flutter so long vowels don't freeze the mouth
    flutter = 0.85 + 0.15 * np.sin(np.arange(len(out)) * 1.9)
    return np.clip(out * flutter, 0, 1)


def main():
    script_path = sys.argv[1]
    stills_only = '--stills' in sys.argv
    sc = json.load(open(script_path))
    vid = sc['id']
    work = os.path.join(ROOT, 'out', vid)
    os.makedirs(work, exist_ok=True)

    vcfg = dict(VOICE, **sc.get('voice', {}))
    for a in sys.argv:
        if a.startswith('--voice='):
            vcfg['voice'] = a.split('=', 1)[1]
    resolve_photos(sc)
    full, words, spans = tokenize(sc['segments'])
    d = tts(full, os.path.join(ROOT, 'cache', 'tts'), vcfg)
    al = d['alignment']
    chars, st, en = al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']
    if ''.join(chars) != full:
        # fall back to proportional mapping if the service normalised the text
        n = len(chars)
        st = [st[min(n - 1, int(i * n / len(full)))] for i in range(len(full))]
        en = [en[min(n - 1, int(i * n / len(full)))] for i in range(len(full))]
        chars = list(full)
    import base64
    raw = os.path.join(work, 'voice_raw.mp3')
    open(raw, 'wb').write(base64.b64decode(d['audio_base64']))
    vchain = 'highpass=f=70,acompressor=threshold=0.25:ratio=2.5:attack=5:release=80'
    if vcfg.get('pitch', 1.0) != 1.0:
        vchain = f"rubberband=pitch={vcfg['pitch']}:formant=preserved," + vchain
    voice_wav = os.path.join(work, 'voice.wav')
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af', vchain, '-ar', '44100', '-ac', '1', voice_wav])
    voice = voice_wav
    with wave.open(voice) as w:
        vdur = w.getnframes() / w.getframerate()

    for w in words:
        w['t0'] = round(LEAD + st[w['c0']], 3)
        w['t1'] = round(LEAD + en[w['c1']], 3)
        w['cap'] = w['seg'] > 0
    segs = []
    for si, seg in enumerate(sc['segments']):
        a, b = spans[si]
        segs.append({'t0': round(LEAD + st[a], 3), 't1': round(LEAD + en[b], 3), 'pose': seg.get('pose', 'idle'),
                     'emote': seg.get('emote', 'happy'), 'card': seg.get('card'), 'happyEyes': seg.get('happyEyes', False)})
    speech_end = LEAD + en[len(full) - 1]
    has_end = sc.get('end', True)
    end_t0 = round(speech_end + 0.35, 3) if has_end else 9999
    duration = round((end_t0 + END_DUR) if has_end else speech_end + 0.6, 3)
    n_frames = int(np.ceil(duration * FPS)) + 1

    env = envelope(voice, n_frames)
    lead_f = int(round(LEAD * FPS))
    mouth = np.zeros(n_frames)
    mouth[lead_f:] = env[: n_frames - lead_f]
    vowel = ['n'] * n_frames
    ci = 0
    for f in range(n_frames):
        t = f / FPS - LEAD
        while ci < len(full) - 1 and en[ci] < t:
            ci += 1
        if 0 <= t <= en[-1]:
            vowel[f] = VOWEL.get(full[ci].lower(), 'n')

    tl = {
        'fps': FPS, 'duration': duration, 'bg': sc.get('bg', 'blue'), 'mascotTheme': sc.get('mascot', 'dark'),
        'hook': {'text': sc['hook'], 't0': 0.0, 't1': segs[0]['t1'], 'photo': sc.get('_hook_photo'), 'emoji': sc.get('hook_emoji')},
        'words': words, 'segments': segs, 'mouth': [round(float(m), 3) for m in mouth], 'vowel': vowel,
        'end': {'t0': end_t0, 'cta': sc.get('cta', 'Безплатна оферта до 24 ч.'), 'url': 'smartmenukj.com',
                'mode': sc.get('end_mode') or ('follow' if 'оследвай' in sc.get('cta', '') else 'offer'),
                'sub': sc.get('end_sub', 'Нов трик всеки ден 💪')},
    }
    tl_path = os.path.join(work, 'timeline.json')
    json.dump(tl, open(tl_path, 'w'), ensure_ascii=False)

    cover = os.path.join(work, 'still_%d.png')
    times = [0.9] + [round((s['t0'] + s['t1']) / 2, 2) for s in segs[1:]] + ([end_t0 + 1.2] if has_end else [])
    run(['node', os.path.join(SRC, 'render.js'), tl_path, '-', '--still', ','.join(map(str, times)), cover])
    if stills_only:
        print(json.dumps({'stills': [cover.replace('%d', str(i)) for i in range(len(times))], 'duration': duration}))
        return

    music = os.path.join(work, 'music.wav')
    run(['python3', os.path.join(SRC, 'audio.py'), 'music', music, str(duration), sc.get('music', 'bounce')])
    sfx_dir = os.path.join(ROOT, 'cache', 'sfx')
    if not os.path.exists(os.path.join(sfx_dir, 'pop.wav')):
        run(['python3', os.path.join(SRC, 'audio.py'), 'sfx', sfx_dir])
    events = [('whoosh', 0.0, 0.55), ('whoosh', segs[0]['t1'], 0.4)]
    events += [('pop', max(0, s['t0'] - 0.15), 0.55) for s in segs[1:] if s.get('card')]
    if has_end:
        events += [('boing', end_t0, 0.45), ('ding', end_t0 + 0.25, 0.5)]

    silent = os.path.join(work, 'silent.mp4')
    subprocess.run(['node', os.path.join(SRC, 'render.js'), tl_path, silent], check=True)

    final = os.path.join(work, f'{vid}.mp4')
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', silent, '-i', voice, '-i', music]
    for name, _, _ in events:
        cmd += ['-i', os.path.join(sfx_dir, name + '.wav')]
    lead_ms = int(LEAD * 1000)
    fc = [f'[1:a]adelay={lead_ms}|{lead_ms},aformat=channel_layouts=stereo,apad=whole_dur={duration},asplit=2[v1][v2]',
          '[2:a]volume=0.30[m]', '[m][v1]sidechaincompress=threshold=0.04:ratio=8:attack=15:release=350[md]']
    mix = ['[v2]', '[md]']
    for i, (_, at, vol) in enumerate(events):
        ms = int(at * 1000)
        fc.append(f'[{3 + i}:a]adelay={ms}|{ms},volume={vol}[s{i}]')
        mix.append(f'[s{i}]')
    fc.append(''.join(mix) + f'amix=inputs={len(mix)}:normalize=0:duration=longest,loudnorm=I=-14:TP=-1.5:LRA=11[a]')
    cmd += ['-filter_complex', ';'.join(fc), '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
            '-ar', '44100', '-t', str(duration), '-movflags', '+faststart', final]
    run(cmd)
    meta = {k: sc.get(k) for k in ('id', 'hook', 'caption', 'hashtags', 'service', 'hook_style')}
    meta.update({'duration': duration, 'file': final})
    json.dump(meta, open(os.path.join(work, 'meta.json'), 'w'), ensure_ascii=False, indent=2)
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == '__main__':
    main()
