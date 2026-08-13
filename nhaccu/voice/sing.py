"""sing — engine hat

Trich nguyen van tu `greeplib/singer.py` cua geese-3d-country.
Chua: `PHON`, `DIPH`, `BW`, `STYLES`, `_reson`, `_expand`, `_glottal`, `_duck_band`, `_tame`, `sing`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from scipy import signal as sg
from .._dsp import SR, _bp, _hp, _lp, sat
from .._core import hz


# code: (F1..F4), (A1..A4), voiced, noise, fixed_dur (None = stretchable)
PHON = {
    # --- vowels (male formant set) --------------------------------------
    'a':  ((730, 1090, 2440, 3400), (1.00, 0.72, 0.42, 0.22), 1, 0.00, None),  # father
    'A':  ((660, 1720, 2410, 3300), (1.00, 0.92, 0.50, 0.24), 1, 0.00, None),  # cat
    'E':  ((530, 1840, 2480, 3400), (1.00, 0.95, 0.55, 0.26), 1, 0.00, None),  # bed
    'i':  ((270, 2290, 3010, 3700), (1.00, 0.70, 0.62, 0.32), 1, 0.00, None),  # see
    'I':  ((390, 1990, 2550, 3400), (1.00, 0.80, 0.52, 0.24), 1, 0.00, None),  # sit
    'o':  ((450,  840, 2400, 3300), (1.00, 0.62, 0.32, 0.16), 1, 0.00, None),  # go (1st half)
    'O':  ((570,  840, 2410, 3300), (1.00, 0.70, 0.36, 0.18), 1, 0.00, None),  # law
    'u':  ((300,  870, 2240, 3300), (1.00, 0.55, 0.26, 0.13), 1, 0.00, None),  # boot
    'U':  ((440, 1020, 2240, 3300), (1.00, 0.66, 0.34, 0.16), 1, 0.00, None),  # book
    'V':  ((640, 1190, 2390, 3300), (1.00, 0.78, 0.40, 0.20), 1, 0.00, None),  # cup
    '@':  ((500, 1400, 2400, 3300), (1.00, 0.80, 0.42, 0.21), 1, 0.00, None),  # schwa
    'R':  ((490, 1350, 1690, 3300), (1.00, 0.88, 0.90, 0.18), 1, 0.00, None),  # her
    # --- voiced continuants ---------------------------------------------
    'm':  ((260,  900, 2200, 3000), (0.72, 0.16, 0.08, 0.03), 1, 0.00, 0.070),
    'n':  ((260, 1600, 2500, 3200), (0.68, 0.24, 0.12, 0.05), 1, 0.00, 0.065),
    'ng': ((260, 2000, 2650, 3300), (0.64, 0.28, 0.14, 0.06), 1, 0.00, 0.085),
    'l':  ((340,  880, 2600, 3300), (0.92, 0.44, 0.30, 0.12), 1, 0.00, 0.055),
    'r':  ((400, 1120, 1560, 3200), (0.92, 0.74, 0.70, 0.12), 1, 0.00, 0.055),
    'w':  ((280,  620, 2200, 3200), (0.88, 0.44, 0.20, 0.09), 1, 0.00, 0.050),
    'y':  ((270, 2300, 3000, 3700), (0.88, 0.66, 0.50, 0.24), 1, 0.00, 0.045),
    'v':  ((310, 1080, 2350, 3300), (0.60, 0.44, 0.26, 0.14), 1, 0.30, 0.050),
    'z':  ((300, 1380, 2550, 5400), (0.40, 0.28, 0.24, 0.50), 1, 0.75, 0.070),
    'dh': ((310, 1280, 2550, 4100), (0.55, 0.40, 0.28, 0.50), 1, 0.35, 0.040),
    'zh': ((310, 1750, 2550, 3400), (0.42, 0.46, 0.42, 0.70), 1, 0.55, 0.065),
    'j':  ((310, 1750, 2550, 3400), (0.45, 0.46, 0.42, 0.72), 1, 0.55, 0.060),
    # --- voiced stops ----------------------------------------------------
    'b':  ((240,  780, 2200, 3000), (0.55, 0.20, 0.11, 0.05), 1, 0.10, 0.035),
    'd':  ((260, 1700, 2550, 3300), (0.50, 0.32, 0.20, 0.20), 1, 0.20, 0.032),
    'g':  ((270, 1850, 2350, 3200), (0.50, 0.34, 0.24, 0.16), 1, 0.20, 0.035),
    # --- unvoiced --------------------------------------------------------
    's':  ((900, 3200, 5600, 7400), (0.02, 0.08, 0.38, 0.52), 0, 1.00, 0.085),
    'sh': ((900, 2000, 3100, 4300), (0.05, 0.44, 0.55, 0.28), 0, 1.00, 0.090),
    'f':  ((900, 2400, 4800, 6800), (0.04, 0.12, 0.26, 0.30), 0, 1.00, 0.070),
    'th': ((900, 2600, 5200, 7000), (0.04, 0.10, 0.22, 0.26), 0, 1.00, 0.060),
    'h':  ((560, 1500, 2500, 3300), (0.45, 0.38, 0.24, 0.14), 0, 1.00, 0.055),
    't':  ((900, 2900, 4200, 6200), (0.05, 0.24, 0.48, 0.34), 0, 1.00, 0.030),
    'k':  ((900, 1850, 2850, 4200), (0.10, 0.50, 0.42, 0.20), 0, 1.00, 0.032),
    'p':  ((680, 1150, 2150, 3200), (0.30, 0.33, 0.19, 0.11), 0, 1.00, 0.028),
    'ch': ((900, 2000, 3100, 4300), (0.05, 0.42, 0.52, 0.28), 0, 1.00, 0.075),
}


DIPH = {
    'aI': ('a', 'I', 0.62), 'aU': ('a', 'U', 0.62), 'eI': ('E', 'i', 0.60),
    'oU': ('o', 'u', 0.62), 'OI': ('O', 'I', 0.60), 'yu': ('y', 'u', 0.30),
    'Ir': ('i', 'R', 0.55), 'Er': ('E', 'R', 0.55), 'Ur': ('U', 'R', 0.55),
}


# Bề rộng dải của bốn bộ cộng hưởng formant.
# Hẹp quá thì Q cao (1990/110 ~ 18) và bộ lọc ngân lên thành một bướu nhọn cố
# định trong phổ -- đo được +11.6 dB so với đường bao ở 1981 Hz. Thanh quản
# thật không nhọn như vậy, vì formant luôn di chuyển; ở đây formant đứng yên
# trong từng đoạn nên cái bướu đứng yên theo và tai nghe ra tiếng chói.
BW = (95.0, 145.0, 200.0, 290.0)


# style -> (open quotient, breath, vib depth cents, vib rate, attack, drive)
STYLES = {
    'croon':    (0.62, 0.075, 24.0, 5.1, 0.030, 1.10),
    'declaim':  (0.52, 0.050, 10.0, 5.6, 0.016, 1.25),
    'shout':    (0.44, 0.045,  8.0, 6.2, 0.010, 1.55),
    'soft':     (0.70, 0.130, 18.0, 4.8, 0.045, 1.00),
    'falsetto': (0.78, 0.170, 30.0, 5.8, 0.035, 1.00),
    'whisper':  (0.62, 1.000,  6.0, 5.0, 0.030, 1.00),
    'gang':     (0.48, 0.060, 12.0, 5.4, 0.012, 1.40),
}


def _reson(x, fc, bw):
    """Peak-normalised 2-pole resonator."""
    fc = float(np.clip(fc, 90.0, SR * 0.45))
    r = np.exp(-np.pi * bw / SR)
    th = 2 * np.pi * fc / SR
    a = [1.0, -2.0 * r * np.cos(th), r * r]
    b0 = (1 - r) * np.sqrt(max(1 - 2 * r * np.cos(2 * th) + r * r, 1e-9))
    return sg.lfilter([b0], a, x)


def _expand(syl):
    """'k-V-m' -> [(phoneme, fixed_dur|None, stretch_weight), ...]"""
    segs = []
    for tok in str(syl).split('-'):
        if not tok:
            continue
        if tok in DIPH:
            a, b, r = DIPH[tok]
            segs.append((a, None, r))
            segs.append((b, None, 1.0 - r))
        elif tok in PHON:
            segs.append((tok, PHON[tok][4], 1.0))
        else:
            segs.append(('@', None, 1.0))
    return segs


def _glottal(f0_arr, L, oq, seed):
    """Raised-sine glottal flow -> derivative -> lip radiation."""
    R = np.random.default_rng(seed)
    step = np.maximum(f0_arr / SR, 1e-9)
    p = np.cumsum(step)
    cycle = np.floor(p).astype(np.int64)
    ncyc = int(cycle[-1]) + 2
    jit = R.normal(0, 0.006, ncyc)          # per-cycle pitch jitter
    ph = (p + jit[np.clip(cycle, 0, ncyc - 1)]) % 1.0
    g = np.where(ph < oq, np.sin(np.pi * np.clip(ph, 0, oq) / oq) ** 2, 0.0)
    d = np.empty(L)
    d[0] = 0.0
    d[1:] = (g[1:] - g[:-1]) / step[1:]
    d *= 0.22
    return sg.lfilter([1.0, -0.90], [1.0], d)


def _duck_band(x, body, lo, hi, thresh, amount, floor):
    """Pull one band down only while it is running away from the body."""
    band = _bp(x, lo, hi, 2)
    e = _lp(np.abs(band), 45, 2)
    b = _lp(np.abs(body), 25, 2) + 1e-6
    g = np.clip(1.0 - amount * np.clip((e/b - thresh) / max(thresh, 1e-6), 0, 1),
                floor, 1.0)
    return x - band * (1.0 - _lp(g, 120, 2))


def _tame(x):
    """Two dynamic bands, not one.

    The old version only watched 5.2-9.5 kHz, so it caught /s/ and /z/ and
    missed the thing that actually hurts: short bursts at 4-5.5 kHz from
    /t/, /k/ and /ch/. Measured, that band ran +9.9 dB ABOVE the body of the
    voice at its worst -- and both the lead chain and the master bus boost
    right through there, so it got amplified three times on the way out.

    Both bands are dynamic. Nothing is removed when the voice is not shouting.
    """
    body = _bp(x, 300, 3000, 2)
    x = _duck_band(x, body, 2300, 5400, thresh=0.42, amount=0.55, floor=0.35)
    x = _duck_band(x, body, 5200, 9500, thresh=0.55, amount=0.75, floor=0.18)
    return x


def sing(midi, dur, syl, vel=1.0, style='croon', seed=0, glide_from=None,
         fshift=1.0, breath=None, vib=None, growl=0.0, cons=1.0, cgain=1.0):
    """Render one sung syllable.

    Returns (audio, preroll_samples).  `preroll` is how far the onset
    consonants stick out BEFORE the beat, so the vowel -- not the 'k' -- lands
    on the downbeat, which is what real singers do and what makes synthesized
    singing suddenly sound like it means it.
    """
    segs = _expand(syl)
    if not segs:
        return np.zeros(8), 0
    oq, br, vibd, vibr, atk, drive = STYLES.get(style, STYLES['croon'])
    if breath is not None:
        br = breath
    if vib is not None:
        vibd = vib

    # ---- allocate time to each phoneme --------------------------------
    # `cons` keo dai cac phu am co do dai co dinh. Do duoc: o cons=1.0 mot cau
    # hat cham roi ra khoi Whisper la "the neighbor is a man" thay vi "the
    # weather is a debt" -- nguyen am dung, phu am bien mat het. Phu am chi
    # chiem ~15% do dai am tiet, va o tempo bai hat thi con it hon nua.
    cons = float(np.clip(cons, 0.5, 3.0))
    fixed = sum(s[1] for s in segs if s[1] is not None) * cons
    wsum = sum(s[2] for s in segs if s[1] is None)
    body = dur + 0.04
    free = max(0.070, body - fixed)
    plan = [(ph, fd * cons if fd is not None else free * (w / max(wsum, 1e-9)))
            for ph, fd, w in segs]

    pre = 0.0
    for i, (ph, fd, w) in enumerate(segs):
        if fd is None:
            break
        pre += plan[i][1]
    pre = min(pre, 0.17)

    total = sum(p[1] for p in plan)
    rel = 0.055
    L = int((total + rel) * SR) + 8
    if L < 32:
        return np.zeros(32), 0
    t = np.arange(L) / SR

    # ---- pitch contour -------------------------------------------------
    f0 = hz(midi)
    f = np.full(L, f0)
    if glide_from is not None:
        gt = min(0.060, dur * 0.35)
        gn = max(int(gt * SR), 2)
        s = np.linspace(0, 1, gn)
        s = s * s * (3 - 2 * s)
        f[:gn] = hz(glide_from) * (1 - s) + f0 * s
    R = np.random.default_rng(4000 + seed * 7 + int(midi))
    onset = np.clip((t - min(0.26, dur * 0.42)) / 0.30, 0, 1)
    vibrato = vibd * onset * np.sin(2 * np.pi * vibr * (1 + 0.05 * np.sin(2 * np.pi * 0.6 * t)) * t
                                    + R.uniform(0, 6))
    drift = 3.0 * np.sin(2 * np.pi * 0.37 * t + R.uniform(0, 6))
    f = f * 2 ** ((vibrato + drift) / 1200.0)
    if growl:
        f = f * (1 + 0.008 * growl * np.sin(2 * np.pi * 26.0 * t))

    # ---- source --------------------------------------------------------
    voiced = _glottal(f, L, oq, seed * 31 + 11)
    noise = R.standard_normal(L)

    # ---- per-segment voiced/noise gains, then filter each span ----------
    # Each phoneme is filtered with static resonators and OVERLAP-crossfaded
    # into the one before it.  The overlap matters: butting the segments end to
    # end and fading each one out before fading the next one in leaves a notch
    # at every phoneme boundary, which is heard as a stutter on every syllable.
    # Every phoneme has ONE printed formant target, so F2 lands on the same
    # few frequencies all song and the long-term spectrum grows a narrow bump
    # there -- measured +11 dB above the envelope at 1981 Hz, right where the
    # ear is most sensitive. A real mouth never repeats a vowel exactly. So
    # each segment gets its own small, deterministic offset, which smears the
    # bump out without changing which vowel you hear.
    fj = 1.0 + R.normal(0, 0.030, (len(plan), 4)) * np.array([0.7, 1.0, 1.0, 1.2])
    out = np.zeros(L)
    pos = 0
    for k, (ph, d) in enumerate(plan):
        n = max(int(d * SR), 2)
        F, A, vg, ng, fd = PHON[ph]
        F = [v * fshift * fj[k, i] for i, v in enumerate(F)]
        stop = (fd is not None and fd < 0.05)
        xf = int((0.008 if stop else 0.028) * SR)
        s1 = min(pos + n, L)
        start = max(pos - xf, 0) if k > 0 else 0
        ov = pos - start
        if start >= s1:
            pos += n
            continue
        pad = int(0.014 * SR)
        a0 = max(start - pad, 0)
        src = voiced[a0:s1] * vg + noise[a0:s1] * (ng * 0.85 + br * vg)
        y = np.zeros(s1 - a0)
        signs = (1.0, -0.95, 0.90, -0.85)
        for fi in range(4):
            y += _reson(src, F[fi], BW[fi]) * A[fi] * signs[fi]
        # `cgain` nhan rieng phu am (khong phai nguyen am). Trong hat that,
        # ca si ep hoi manh hon o phu am de chu nghe ra tren nen nhac; o day
        # phai lam bang tay vi mo hinh khong co co bung.
        if fd is not None and cgain != 1.0:
            y = y * (1.0 + (cgain - 1.0) * (1.6 if vg < 0.7 else 0.8))
        seg = y[start - a0:]
        if ov > 1:
            fade = np.sqrt(np.linspace(0.0, 1.0, ov))
            out[start:pos] *= np.sqrt(np.linspace(1.0, 0.0, ov))
            seg = seg.copy()
            seg[:ov] *= fade
        out[start:s1] += seg
        pos += n
        if pos >= L:
            break

    # ---- amplitude ------------------------------------------------------
    amp = np.ones(L)
    at = max(int(atk * SR), 1)
    rl = max(int(rel * SR), 1)
    amp[:at] = np.linspace(0, 1, at) ** 0.7
    amp[-rl:] *= np.linspace(1, 0, rl) ** 1.4
    amp *= 0.88 + 0.12 * np.sin(np.pi * np.linspace(0, 1, L))

    out = out * amp
    out = _hp(out, 60, 2)
    out = _tame(out)
    out = _lp(out, 9500, 2)
    out = sat(out, drive, 0.35)

    # Normalise on RMS, not peak.  Peak-normalising every syllable pushes any
    # syllable whose loudest moment is an /s/ up until the sibilance is the
    # loudest thing on the record.
    r = float(np.sqrt(np.mean(out * out) + 1e-20))
    if r > 1e-7:
        out = out * (0.135 / r) * vel
    pk = float(np.max(np.abs(out)))
    if pk > 0.85:
        out = np.tanh(out / pk * 1.2) * (pk / 1.2) * (0.85 / pk)
    return out, int(pre * SR)
