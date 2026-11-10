"""Procedural, royalty-free background music and sound effects (numpy only).

python3 src/audio.py music <out.wav> <seconds> <style>   # style: bounce | chill | hype
python3 src/audio.py sfx <out_dir>
"""
import sys, wave
import numpy as np

SR = 44100


def write_wav(path, x):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    peak = np.max(np.abs(x)) or 1.0
    x = x / peak * 0.89
    data = (x * 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def env_adsr(n, a=0.005, d=0.08, s=0.6, r=0.1):
    t = np.arange(n) / SR
    dur = n / SR
    e = np.ones(n) * s
    e[t < a] = t[t < a] / a
    m = (t >= a) & (t < a + d)
    e[m] = 1 - (1 - s) * (t[m] - a) / d
    rel = t > dur - r
    e[rel] *= np.clip((dur - t[rel]) / r, 0, 1)
    return e


def note_hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def pluck(freq, dur, bright=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * freq * t) + 0.5 * bright * np.sin(2 * np.pi * 2 * freq * t)
         + 0.25 * bright * np.sin(2 * np.pi * 3 * freq * t + 0.3))
    return x * np.exp(-t * 7.5) * env_adsr(n, 0.003, 0.05, 1.0, 0.03)


def pad(freqs, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for f in freqs:
        for det in (-0.12, 0.0, 0.12):
            ph = np.random.rand() * 6.28
            ff = f * 2 ** (det / 12)
            x += np.sign(np.sin(2 * np.pi * ff * t + ph)) * 0.15 + np.sin(2 * np.pi * ff * t + ph) * 0.5
    k = np.ones(40) / 40  # crude low-pass
    x = np.convolve(x, k, mode='same')
    return x * env_adsr(n, 0.25, 0.3, 0.8, 0.4)


def bass(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * 2 * freq * t)
    return np.tanh(1.6 * x) * env_adsr(n, 0.004, 0.1, 0.7, 0.05)


def kick():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 50 + 110 * np.exp(-t * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9)


def snare():
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    noise = np.random.randn(n)
    noise = noise - np.convolve(noise, np.ones(6) / 6, mode='same')
    return (0.7 * noise * np.exp(-t * 18) + 0.5 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25))


def hat(open_=False):
    n = int((0.18 if open_ else 0.05) * SR)
    t = np.arange(n) / SR
    noise = np.random.randn(n)
    noise = noise - np.convolve(noise, np.ones(3) / 3, mode='same')
    return noise * np.exp(-t * (14 if open_ else 70)) * 0.35


def clap():
    n = int(0.2 * SR)
    t = np.arange(n) / SR
    noise = np.random.randn(n)
    e = np.exp(-t * 22)
    for k in (0.0, 0.012, 0.024):
        e += np.exp(-np.maximum(t - k, 0) * 120) * (t >= k)
    return noise * e * 0.3


STYLES = {
    # bpm, root midi, progression (scale degrees as semitone offsets of chord roots), chord quality
    'bounce': dict(bpm=112, root=60, prog=[0, 7, 9, 5], minor=[False, False, True, False], swing=0.0),
    'chill': dict(bpm=92, root=57, prog=[0, 5, 3, 10], minor=[True, False, False, False], swing=0.12),
    'hype': dict(bpm=124, root=62, prog=[0, 10, 8, 7], minor=[True, False, False, False], swing=0.0),
}


def make_music(path, seconds, style='bounce', seed=1):
    np.random.seed(seed)
    st = STYLES.get(style, STYLES['bounce'])
    beat = 60.0 / st['bpm']
    total = int((seconds + 1) * SR)
    L = np.zeros(total)
    R = np.zeros(total)

    def add(sig, at, gain=1.0, pan=0.0):
        i = int(at * SR)
        if i >= total:
            return
        j = min(total, i + len(sig))
        L[i:j] += sig[:j - i] * gain * (1 - max(0, pan))
        R[i:j] += sig[:j - i] * gain * (1 + min(0, pan))

    bars = int(np.ceil(seconds / (4 * beat))) + 1
    K, S, H, HO, C = kick(), snare(), hat(), hat(True), clap()
    for b in range(bars):
        ci = b % len(st['prog'])
        root = st['root'] + st['prog'][ci]
        minor = st['minor'][ci]
        triad = [root, root + (3 if minor else 4), root + 7]
        t0 = b * 4 * beat
        intro = b < 1
        add(pad([note_hz(m) for m in triad], 4 * beat), t0, 0.10)
        for k in range(8):  # eighth notes
            tt = t0 + k * beat / 2 + (st['swing'] * beat / 2 if k % 2 else 0)
            if not intro:
                add(H if k % 2 == 0 else H * 0.6, tt, 0.5, pan=0.3)
            arp = triad[[0, 1, 2, 1, 0, 2, 1, 2][k]] + 12
            if k in (0, 3, 4, 6) or style == 'hype':
                add(pluck(note_hz(arp), beat * 0.45, 0.8), tt, 0.20, pan=-0.25)
        for k in range(4):
            tt = t0 + k * beat
            if not intro or k == 0:
                add(K, tt, 0.9)
            if k in (1, 3) and not intro:
                add(S, tt, 0.35)
                add(C, tt, 0.25)
            add(bass(note_hz(root - 24), beat * 0.9), tt, 0.32)
        if not intro and style != 'chill':
            add(HO, t0 + 3.5 * beat, 0.4, pan=0.3)
    x = np.stack([L, R], axis=1)[: int(seconds * SR)]
    fade = int(1.2 * SR)
    x[-fade:] *= np.linspace(1, 0, fade)[:, None]
    write_wav(path, x)


def make_sfx(out):
    import os
    os.makedirs(out, exist_ok=True)
    # pop: quick upward blip
    n = int(0.12 * SR); t = np.arange(n) / SR
    f = 500 + 900 * (t / t[-1])
    write_wav(f'{out}/pop.wav', np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30))
    # whoosh: band-passed noise swell
    n = int(0.45 * SR); t = np.arange(n) / SR
    noise = np.random.randn(n)
    lp = np.convolve(noise, np.ones(12) / 12, mode='same')
    hp = lp - np.convolve(lp, np.ones(60) / 60, mode='same')
    e = np.sin(np.pi * t / t[-1]) ** 2
    write_wav(f'{out}/whoosh.wav', hp * e)
    # ding: bell
    n = int(0.9 * SR); t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * 1318.5 * m * t) * np.exp(-t * d) for a, m, d in [(1, 1, 5), (0.5, 2.0, 8), (0.25, 3.01, 11)])
    write_wav(f'{out}/ding.wav', x)
    # boing: springy pitch wobble for the flex / jump
    n = int(0.5 * SR); t = np.arange(n) / SR
    f = 220 + 160 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 5) + 120 * t
    write_wav(f'{out}/boing.wav', np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6))


if __name__ == '__main__':
    if sys.argv[1] == 'music':
        make_music(sys.argv[2], float(sys.argv[3]), sys.argv[4] if len(sys.argv) > 4 else 'bounce')
    else:
        make_sfx(sys.argv[2])
