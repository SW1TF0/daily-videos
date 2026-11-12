"""Build one vertical video from a script JSON.

python3 src/build.py scripts/<name>.json            -> out/<id>/<id>.mp4
python3 src/build.py scripts/<name>.json --stills   -> only preview stills (no full render)

Script format (see scripts/test/*.json):
  hook, hook_emoji, bg, mascot, music (procedural fallback style), music_prompt (ElevenLabs music),
  cast: {id: {voice, name, emoji, role, color}}  -> extra characters for skits (Plochko is "plochko")
  segments: [{say, speaker, pose, emote, card, sfx, happyEyes}], cta, caption, hashtags
"""
import base64, hashlib, json, os, re, subprocess, sys, time, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src')
CACHE = os.path.join(ROOT, 'cache')
FPS = 30
SR = 44100
LEAD = 0.45        # seconds before the first word (hook slam)
GAP_SAME = 0.12    # pause between consecutive lines of the same speaker
GAP_SWITCH = 0.32  # pause when the speaker changes (comic timing)
END_DUR = 2.4      # end card length
VOICES = {  # native Bulgarian voices from the ElevenLabs library (added to the account)
    'mimi': 'CBDgRB8OyxYGowoi5iXR', 'nadya': 'mW3jGQPMrIgiOavQfIhc', 'elena': 'fSxb5mPM1l5zTVVtM3Vb',
    'nikolay': 'jFUMfgSnXMVNWDwPdkDf', 'georgi': '31jwlwrRwpOA5yGuVAby',
    'boris': 'UcGGwCMBEQAIYpXt4nTS', 'peter': '406EiNlYvqFqcz3vsnOm', 'georgi_ads': 'Ywe24jn5elUzaO9vm6vG',
    'kosta': 'gdk0ZsvfAOobfbTtnx6p', 'yordan': 'vZifugoCmJjNgn0bBdKH',
}
VOICE = {'voice': 'nikolay', 'model_id': 'eleven_v4', 'pitch': 1.0, 'settings': {'stability': 0.5}}
# how brand words are spoken (captions keep the written form)
PRON = {'SmartMenuKJ': 'Смарт Меню Кей Джей', '4G': 'фор джи', 'QR': 'кю ар', 'IP': 'ай пи', 'PC': 'пи си', '3D': 'три ди'}
VOWEL = {**{c: 'a' for c in 'ая'}, **{c: 'e' for c in 'еий'}, **{c: 'o' for c in 'оую'}}
MUSIC_PROMPTS = {
    'bounce': 'Upbeat playful modern pop instrumental for a funny short social media video, bouncy bass, plucks, claps, cheeky and happy, 112 bpm, no vocals',
    'chill': 'Warm lo-fi chill hop instrumental, soft keys, mellow drums, cozy and positive, 90 bpm, no vocals',
    'hype': 'Energetic punchy electronic trap-pop instrumental, tense build and confident groove, 128 bpm, no vocals',
    'comedy': 'Quirky comedic instrumental, pizzicato strings, bassoon, playful cartoon timing, light percussion, no vocals',
    'mystery': 'Mysterious cinematic legend-telling instrumental, low pulses, plucked strings, light suspense that turns playful, no vocals',
}
SFX_FILES = {'pop', 'whoosh', 'ding', 'boing'}  # procedural ones in cache/sfx


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        sys.stderr.write(r.stdout[-2000:] + r.stderr[-2000:])
        raise SystemExit(f'command failed: {cmd[0]} {" ".join(map(str, cmd[1:4]))}')
    return r.stdout


def key_of(*parts):
    return hashlib.sha1(json.dumps(parts, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:16]


def el_post(path, body, out, timeout=240):
    """POST to the ElevenLabs API (key injected by the proxy); returns the HTTP status."""
    r = subprocess.run(['curl', '-sS', '--retry', '2', '--retry-delay', '5', '--max-time', str(timeout), '-X', 'POST',
                        f'https://api.elevenlabs.io{path}', '-H', 'xi-api-key: proxy-injected', '-H', 'Content-Type: application/json',
                        '-d', json.dumps(body, ensure_ascii=False), '-o', out, '-w', '%{http_code}'], capture_output=True, text=True)
    return int(r.stdout or 0)


# ---------------------------------------------------------------- voice
def tts(text, voice):
    d = os.path.join(CACHE, 'tts')
    os.makedirs(d, exist_ok=True)
    vid = VOICES.get(voice['voice'], voice['voice'])
    body = {'text': text, 'model_id': voice['model_id'], 'language_code': 'bg', 'voice_settings': voice['settings']}
    path = os.path.join(d, key_of(vid, body) + '.json')
    if not os.path.exists(path):
        code = el_post(f'/v1/text-to-speech/{vid}/with-timestamps?output_format=mp3_44100_128', body, path, 180)
        if code != 200:
            msg = open(path, errors='replace').read()[:400] if os.path.exists(path) else ''
            if os.path.exists(path):
                os.remove(path)
            raise SystemExit(f'TTS failed ({code}): {msg}')
    return json.load(open(path))


def decode_audio(src_bytes_or_path, dst_wav, chain='anull'):
    src = src_bytes_or_path
    if isinstance(src, bytes):
        tmp = dst_wav + '.src.mp3'
        open(tmp, 'wb').write(src)
        src = tmp
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-af', chain, '-ar', str(SR), '-ac', '1', dst_wav])
    with wave.open(dst_wav) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').astype(np.float32) / 32768


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype('<i2').tobytes())


# ---------------------------------------------------------------- generated media (ElevenLabs)
def el_flow(kind, body, ext):
    """Generate an image or video with ElevenLabs flows (Pro plan+). Returns a local path (cached)."""
    d = os.path.join(CACHE, 'gen')
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f'{kind}-{key_of(body)}.{ext}')
    if os.path.exists(path):
        return path
    resp = path + '.json'
    code = el_post(f'/v1/flows/{kind}', body, resp, 120)
    res = json.load(open(resp)) if os.path.exists(resp) else {}
    if code not in (200, 201, 202) or not res.get('id'):
        raise RuntimeError(f'{kind} generation refused ({code}): {str(res)[:300]}')
    gid, t0 = res['id'], time.time()
    while time.time() - t0 < (600 if kind == 'video' else 240):
        time.sleep(5)
        st = json.loads(run(['curl', '-sS', '--max-time', '60', f'https://api.elevenlabs.io/v1/flows/{kind}/{gid}', '-H', 'xi-api-key: proxy-injected']))
        if st.get('status') == 'completed':
            run(['curl', '-sS', '-L', '--fail', '--max-time', '300', st['content_url'], '-o', path])
            return path
        if st.get('status') == 'failed':
            raise RuntimeError(f"{kind} generation failed: {st.get('failure_reason')} {st.get('error_message', '')[:200]}")
    raise RuntimeError(f'{kind} generation timed out')


def gen_image(prompt, aspect):
    return el_flow('image', {'model_id': 'gemini-3.1-flash-image', 'prompt': prompt, 'aspect_ratio': aspect, 'resolution': '2K'}, 'png')


def gen_clip(prompt, aspect, secs):
    secs = min([4, 6, 8], key=lambda s: abs(s - int(secs or 6)))
    return el_flow('video', {'model_id': 'veo-3.1-fast-generate-001', 'prompt': prompt, 'aspect_ratio': aspect, 'duration_secs': secs,
                             'resolution': '1080p', 'generate_audio': False,
                             'negative_prompt': 'text, captions, watermark, logo, distorted hands'}, 'mp4')


def clip_frames(mp4, work, n, width, secs=None):
    """Extract a clip (generated, or a real video) to numbered JPG frames (30 fps) the renderer can step through;
    `secs` keeps only the start of a longer video."""
    d = os.path.join(work, f'clip{n}')
    os.makedirs(d, exist_ok=True)
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', mp4, *(['-t', str(secs)] if secs else []),
         '-vf', f'fps={FPS},scale={width}:-2', '-q:v', '3', os.path.join(d, '%05d.jpg')])
    count = len([f for f in os.listdir(d) if f.endswith('.jpg')])
    return {'dir': 'file://' + d, 'count': count}


def resolve_media(sc, work):
    """Replace generation requests in the script with local files; fall back to illustrated cards on failure."""
    notes = []

    def attempt(fn, *a):
        try:
            return fn(*a)
        except Exception as e:  # e.g. ElevenLabs plan below Pro: keep building without it
            notes.append(str(e)[:200])
            sys.stderr.write(f'media skipped: {e}\n')
            return None

    hp = sc.get('hook_photo') or {}
    if hp.get('src'):
        sc['_hook_photo'] = 'file://' + os.path.join(ROOT, hp['src']) if not hp['src'].startswith('file://') else hp['src']
    elif hp.get('gen'):
        p = attempt(gen_image, hp['gen'], '9:16')
        sc['_hook_photo'] = 'file://' + p if p else None
    hc = sc.get('hook_clip') or {}
    if hc.get('gen'):
        p = attempt(gen_clip, hc['gen'], '9:16', hc.get('secs', 6))
        sc['_hook_clip'] = clip_frames(p, work, 'hook', 1080) if p else None
    def local(src):
        """A file of the repo (e.g. out/media/… from `telegram.py media get`) -> its file:// URL."""
        return src if src.startswith(('file://', 'http://', 'https://')) else 'file://' + os.path.join(ROOT, src)
    for i, seg in enumerate(sc['segments']):
        c = seg.get('card')
        if not c:
            continue
        if c.get('type') == 'photo' and c.get('src'):
            c['src'] = local(c['src'])  # a real photo (the owner's, #плочко)
            if c['src'].startswith('file://') and not os.path.exists(c['src'][7:]):
                notes.append(f"photo card {i}: {c.pop('src')[7:]} is missing (download it with `telegram.py media get`)")
        if c.get('type') == 'clip' and c.get('src') and not c.get('frames'):
            p = c['src'][7:] if c['src'].startswith('file://') else os.path.join(ROOT, c['src'])
            if os.path.exists(p):
                c['frames'] = clip_frames(p, work, i, 900, c.get('secs', 6))  # a real video (the owner's, #плочко)
        if c.get('type') == 'photo' and c.get('gen') and not c.get('src'):
            p = attempt(gen_image, c['gen'], '3:2')
            if p:
                c['src'] = 'file://' + p
        if c.get('type') == 'clip' and c.get('gen'):
            p = attempt(gen_clip, c['gen'], '16:9', c.get('secs', 6))
            if p:
                c['frames'] = clip_frames(p, work, i, 900)
        if c.get('type') in ('photo', 'clip') and not (c.get('src') or c.get('frames')):
            fb = c.get('fallback') or {'type': 'scene', 'icons': c.get('icons') or ['✨'], 'title': c.get('title', '')}
            seg['card'] = fb
    return notes


# ---------------------------------------------------------------- music & sfx
def gen_music(prompt, seconds):
    d = os.path.join(CACHE, 'music')
    os.makedirs(d, exist_ok=True)
    ms = int(min(600000, max(10000, (seconds + 1.5) * 1000)))
    body = {'prompt': prompt, 'music_length_ms': ms, 'force_instrumental': True}
    path = os.path.join(d, key_of(body) + '.mp3')
    if not os.path.exists(path):
        code = el_post('/v1/music?output_format=mp3_44100_128', body, path, 300)
        if code != 200:
            if os.path.exists(path):
                os.remove(path)
            raise RuntimeError(f'music failed ({code})')
    return path


def pick_music(sc, duration):
    """Library track from assets/music (no credits, instant) unless the script asks for a custom music_prompt.
    Returns (mp3_path, start_offset_seconds)."""
    if sc.get('music_prompt'):
        return gen_music(sc['music_prompt'], duration), 0.0
    import glob
    style = sc.get('music', 'bounce')
    lib_dir = os.path.join(ROOT, 'assets', 'music')
    lib = sorted(glob.glob(os.path.join(lib_dir, f'{style}-*.mp3'))) or sorted(glob.glob(os.path.join(lib_dir, 'bounce-*.mp3')))
    if not lib:  # first time for this style: compose a 60 s track once and keep it in the repo
        os.makedirs(lib_dir, exist_ok=True)
        src = gen_music(MUSIC_PROMPTS.get(style, MUSIC_PROMPTS['bounce']), 58.5)
        dst = os.path.join(lib_dir, f'{style}-1.mp3')
        import shutil
        shutil.copy(src, dst)
        lib = [dst]
    h = int(hashlib.sha1(sc['id'].encode()).hexdigest(), 16)
    track = lib[h % len(lib)]
    room = max(0.0, 59.0 - duration)
    return track, round((h >> 8) % 1000 / 1000 * min(room, 20.0), 2)


def gen_sfx(text):
    if text in SFX_FILES:
        return os.path.join(CACHE, 'sfx', text + '.wav')
    d = os.path.join(CACHE, 'sfx-el')
    os.makedirs(d, exist_ok=True)
    body = {'text': text, 'duration_seconds': 1.8, 'prompt_influence': 0.6}
    path = os.path.join(d, key_of(body) + '.mp3')
    if not os.path.exists(path):
        code = el_post('/v1/sound-generation?output_format=mp3_44100_128', body, path, 120)
        if code != 200:
            if os.path.exists(path):
                os.remove(path)
            raise RuntimeError(f'sfx failed ({code})')
    return path


# ---------------------------------------------------------------- text
def tokenize(segments):
    """Per segment: words with emphasis flags and the spoken form (brand pronunciations)."""
    out = []
    for si, seg in enumerate(segments):
        text, words = '', []
        for tok in seg['say'].split():
            em = '*' in tok
            clean = tok.replace('*', '')
            if not clean:
                continue
            m = re.match(r'^([^\w]*)(.*?)([^\w]*)$', clean)
            spoken = m.group(1) + PRON.get(m.group(2), m.group(2)) + m.group(3)
            if text:
                text += ' '
            words.append({'w': clean, 'c0': len(text), 'c1': len(text) + len(spoken) - 1, 'seg': si, 'em': em})
            text += spoken
        out.append((text, words))
    return out


def envelope(x, n_frames):
    hop = SR / FPS
    rms = np.zeros(n_frames)
    for i in range(n_frames):
        a, b = int(i * hop - hop / 2), int(i * hop + hop)
        seg = x[max(0, a):max(0, b)]
        rms[i] = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0
    ref = np.percentile(rms[rms > 0], 92) if np.any(rms > 0) else 1
    e = np.clip(rms / ref, 0, 1.2)
    out = np.zeros_like(e)
    for i in range(len(e)):
        prev = out[i - 1] if i else 0
        out[i] = prev + (e[i] - prev) * (0.65 if e[i] > prev else 0.35)
    out[out < 0.12] = 0
    return np.clip(out * (0.85 + 0.15 * np.sin(np.arange(len(out)) * 1.9)), 0, 1)


# ---------------------------------------------------------------- main
def main():
    script_path = sys.argv[1]
    stills_only = '--stills' in sys.argv
    sc = json.load(open(script_path))
    vid = sc['id']
    work = os.path.join(ROOT, 'out', vid)
    os.makedirs(work, exist_ok=True)

    cast = {'plochko': dict(VOICE, **sc.get('voice', {}), name='Плочко')}
    for cid, c in (sc.get('cast') or {}).items():
        cast[cid] = dict(VOICE, voice=c.get('voice', 'boris'), name=c.get('name', cid), emoji=c.get('emoji', '🙂'),
                         role=c.get('role', ''), color=c.get('color', '#ff9f0a'), avatar=None)
        if c.get('gen_avatar'):  # photorealistic portrait for the call bubble (ElevenLabs Pro); emoji otherwise
            try:
                cast[cid]['avatar'] = 'file://' + gen_image(c['gen_avatar'], '1:1')
            except Exception as e:
                sys.stderr.write(f'avatar skipped: {e}\n')
    notes = resolve_media(sc, work)
    segments = sc['segments']
    toks = tokenize(segments)

    # group consecutive segments of the same speaker -> one TTS call each (natural intonation)
    groups = []
    for si, seg in enumerate(segments):
        spk = seg.get('speaker', 'plochko')
        if spk not in cast:
            raise SystemExit(f'unknown speaker {spk!r} in segment {si}')
        if groups and groups[-1]['spk'] == spk:
            groups[-1]['segs'].append(si)
        else:
            groups.append({'spk': spk, 'segs': [si]})

    pieces, words, segs_t, t = [], [], {}, LEAD
    for gi, g in enumerate(groups):
        if gi:
            t += GAP_SWITCH if g['spk'] != groups[gi - 1]['spk'] else GAP_SAME
        text, gwords, offsets = '', [], {}
        for si in g['segs']:
            if text:
                text += ' '
            offsets[si] = len(text)
            text += toks[si][0]
        d = tts(text, cast[g['spk']])
        al = d['alignment']
        chars, st, en = al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']
        if ''.join(chars) != text:  # service normalised the text: map proportionally
            n = len(chars)
            st = [st[min(n - 1, int(i * n / len(text)))] for i in range(len(text))]
            en = [en[min(n - 1, int(i * n / len(text)))] for i in range(len(text))]
        audio = decode_audio(base64.b64decode(d['audio_base64']), os.path.join(work, f'voice_{gi}.wav'),
                             'highpass=f=70,acompressor=threshold=0.25:ratio=2.5:attack=5:release=80')
        pieces.append((t, audio))
        for si in g['segs']:
            o = offsets[si]
            for w in toks[si][1]:
                words.append({'w': w['w'], 'em': w['em'], 'seg': si, 'spk': g['spk'],
                              't0': round(t + st[o + w['c0']], 3), 't1': round(t + en[o + w['c1']], 3)})
            sw = [w for w in words if w['seg'] == si]
            segs_t[si] = (sw[0]['t0'], sw[-1]['t1']) if sw else (t, t + 0.5)
        g['chars'] = (t, text, st, en)
        t += len(audio) / SR
    speech_end = t
    has_end = sc.get('end', True)
    end_t0 = round(speech_end + 0.35, 3) if has_end else 9999
    duration = round((end_t0 + END_DUR) if has_end else speech_end + 0.6, 3)
    n_frames = int(np.ceil(duration * FPS)) + 1

    voice = np.zeros(int((duration + 1) * SR), dtype=np.float32)
    for start, audio in pieces:
        i = int(start * SR)
        voice[i:i + len(audio)] += audio[: len(voice) - i]
    voice_wav = os.path.join(work, 'voice.wav')
    write_wav(voice_wav, voice[: int(duration * SR)])

    env = envelope(voice, n_frames)
    spk = [''] * n_frames
    vowel = ['n'] * n_frames
    for g in groups:
        g0, text, st, en = g['chars']
        ci = 0
        for f in range(int(g0 * FPS), min(n_frames, int((g0 + en[-1]) * FPS) + 2)):
            tt = f / FPS - g0
            spk[f] = g['spk']
            while ci < len(text) - 1 and en[ci] < tt:
                ci += 1
            vowel[f] = VOWEL.get(text[ci].lower(), 'n')
    for w in words:
        w['cap'] = w['seg'] > 0

    segs = []
    for si, seg in enumerate(segments):
        a, b = segs_t[si]
        segs.append({'t0': round(a, 3), 't1': round(b, 3), 'pose': seg.get('pose', 'idle'), 'emote': seg.get('emote', 'happy'),
                     'card': seg.get('card'), 'happyEyes': seg.get('happyEyes', False), 'speaker': seg.get('speaker', 'plochko')})

    guests = {k: {kk: v.get(kk) for kk in ('name', 'emoji', 'role', 'color', 'avatar')} for k, v in cast.items() if k != 'plochko'}
    tl = {
        'fps': FPS, 'duration': duration, 'bg': sc.get('bg', 'blue'), 'mascotTheme': sc.get('mascot', 'dark'),
        'hook': {'text': sc['hook'], 't0': 0.0, 't1': segs[0]['t1'], 'photo': sc.get('_hook_photo'),
                 'clip': sc.get('_hook_clip'), 'emoji': sc.get('hook_emoji')},
        'words': words, 'segments': segs, 'cast': guests, 'spk': spk,
        'mouth': [round(float(m), 3) for m in env], 'vowel': vowel,
        'end': {'t0': end_t0, 'cta': sc.get('cta', 'Безплатна оферта до 24 ч.'), 'url': 'smartmenukj.com',
                'mode': sc.get('end_mode') or ('follow' if 'оследвай' in sc.get('cta', '') else 'offer'),
                'sub': sc.get('end_sub', 'Нов трик всеки ден 💪')},
    }
    tl_path = os.path.join(work, 'timeline.json')
    json.dump(tl, open(tl_path, 'w'), ensure_ascii=False)

    stills = os.path.join(work, 'still_%d.png')
    times = [0.9] + [round((s['t0'] + s['t1']) / 2, 2) for s in segs[1:]] + ([end_t0 + 1.2] if has_end else [])
    run(['node', os.path.join(SRC, 'render.js'), tl_path, '-', '--still', ','.join(map(str, times)), stills])
    if stills_only:
        print(json.dumps({'stills': [stills.replace('%d', str(i)) for i in range(len(times))], 'duration': duration, 'notes': notes}))
        return

    # music: composed by ElevenLabs for this video (fallback: procedural)
    music = os.path.join(work, 'music.wav')
    style = sc.get('music', 'bounce')
    try:
        mp3, offset = pick_music(sc, duration)
        run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(offset), '-i', mp3, '-af',
             f'afade=t=in:st=0:d=0.3,afade=t=out:st={max(0, duration - 1.2)}:d=1.2', '-t', str(duration), '-ar', str(SR), '-ac', '2', music])
        music_vol = 0.22
    except Exception as e:
        notes.append(f'music fallback: {e}')
        run(['python3', os.path.join(SRC, 'audio.py'), 'music', music, str(duration), style if style in ('bounce', 'chill', 'hype') else 'bounce'])
        music_vol = 0.30
    sfx_dir = os.path.join(CACHE, 'sfx')
    if not os.path.exists(os.path.join(sfx_dir, 'pop.wav')):
        run(['python3', os.path.join(SRC, 'audio.py'), 'sfx', sfx_dir])
    events = [('whoosh', 0.0, 0.5), ('whoosh', segs[0]['t1'], 0.35)]
    events += [('pop', max(0, s['t0'] - 0.15), 0.5) for s in segs[1:] if s.get('card')]
    for si, seg in enumerate(segments):
        if seg.get('sfx'):
            events.append((seg['sfx'], max(0, segs[si]['t0'] - 0.1) if seg.get('sfx_at') != 'end' else segs[si]['t1'], float(seg.get('sfx_vol', 0.6))))
    if has_end:
        events += [('boing', end_t0, 0.4), ('ding', end_t0 + 0.25, 0.45)]
    sfx_files = []
    for name, at, vol in events:
        try:
            sfx_files.append((gen_sfx(name), at, vol))
        except Exception as e:
            notes.append(f'sfx skipped ({name}): {e}')

    silent = os.path.join(work, 'silent.mp4')
    subprocess.run(['node', os.path.join(SRC, 'render.js'), tl_path, silent], check=True)

    final = os.path.join(work, f'{vid}.mp4')
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', silent, '-i', voice_wav, '-i', music]
    for path, _, _ in sfx_files:
        cmd += ['-i', path]
    fc = [f'[1:a]aformat=channel_layouts=stereo,apad=whole_dur={duration},asplit=2[v1][v2]',
          f'[2:a]volume={music_vol}[m]', '[m][v1]sidechaincompress=threshold=0.04:ratio=8:attack=15:release=350[md]']
    mix = ['[v2]', '[md]']
    for i, (_, at, vol) in enumerate(sfx_files):
        ms = int(at * 1000)
        fc.append(f'[{3 + i}:a]aformat=channel_layouts=stereo,adelay={ms}|{ms},volume={vol}[s{i}]')
        mix.append(f'[s{i}]')
    fc.append(''.join(mix) + f'amix=inputs={len(mix)}:normalize=0:duration=longest,loudnorm=I=-14:TP=-1.5:LRA=11[a]')
    cmd += ['-filter_complex', ';'.join(fc), '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
            '-ar', str(SR), '-t', str(duration), '-movflags', '+faststart', final]
    run(cmd)
    meta = {k: sc.get(k) for k in ('id', 'hook', 'caption', 'hashtags', 'service', 'hook_style', 'series', 'first_comment')}
    meta.update({'duration': duration, 'file': final, 'notes': notes})
    json.dump(meta, open(os.path.join(work, 'meta.json'), 'w'), ensure_ascii=False, indent=2)
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == '__main__':
    main()
