"""Low-level DSP shared by every module.

Ported from the v6 "NIN" engine, with the fixes from its _fix.py applied
inline rather than as monkey patches.
"""
from __future__ import annotations

import numpy as np
from scipy import signal as sg

SR = 44100
TWO_PI = 2.0 * np.pi


# ------------------------------------------------------------------ filters --

def _lp(x, f, o=2):
    b, a = sg.butter(o, min(f, SR / 2 - 100) / (SR / 2), 'low')
    return sg.lfilter(b, a, x)


def _hp(x, f, o=2):
    b, a = sg.butter(o, max(min(f, SR / 2 - 100), 5) / (SR / 2), 'high')
    return sg.lfilter(b, a, x)


def _bp(x, lo, hi, o=2):
    hi = min(hi, SR / 2 - 100)
    lo = max(lo, 20)
    if lo >= hi:
        return np.zeros_like(x)
    b, a = sg.butter(o, [lo / (SR / 2), hi / (SR / 2)], 'band')
    return sg.lfilter(b, a, x)


def _peak(x, f, q, g):
    """Add a resonant peak at f with gain g (parallel, not shelving)."""
    bq, aq = sg.iirpeak(min(f, SR / 2 - 100) / (SR / 2), q)
    return x + sg.lfilter(bq, aq, x) * g


def _reso_lp(x, cut, res=6.0):
    cut = float(np.clip(cut, 60, SR / 2 - 400))
    y = _lp(x, cut, 4)
    try:
        bq, aq = sg.iirpeak(cut / (SR / 2), max(res, 0.5))
        y = y + sg.lfilter(bq, aq, x) * min(res / 6.0, 2.2)
    except Exception:
        pass
    return y


# --------------------------------------------------------------- envelopes --

def _ramp(x, ms=0.8):
    n = min(int(ms / 1000 * SR), len(x))
    if n > 1:
        x = x.copy()
        x[:n] *= np.linspace(0, 1, n)
    return x


def _fadeout(x, ms=20.0):
    n = min(int(ms / 1000 * SR), len(x))
    if n > 1:
        x = x.copy()
        x[-n:] *= np.linspace(1, 0, n)
    return x


def env(L, a, d, s, r):
    """The engine's workhorse ADSR (linear segments, curved release)."""
    e = np.ones(L)
    ai = min(int(a * SR), L)
    if ai > 0:
        e[:ai] = np.linspace(0, 1, ai)
    di = int(d * SR)
    if ai + di < L:
        e[ai:ai + di] = np.linspace(1, s, di)
        e[ai + di:] = s
    else:
        e[ai:] = np.linspace(1, s, max(L - ai, 1))
    ri = min(int(r * SR), L)
    if ri > 0:
        e[L - ri:] *= np.linspace(1, 0, ri) ** 1.3
    return e


def swell(L, peak_at=0.45, curve=1.7):
    """Brass/bowed swell: rise to a peak inside the note, then relax."""
    p = int(np.clip(peak_at, 0.05, 0.95) * L)
    out = np.empty(L)
    out[:p] = np.linspace(0, 1, p) ** (1.0 / curve)
    out[p:] = np.linspace(1, 0.62, L - p) ** curve
    return out


# ------------------------------------------------------------- oscillators --

def _blpulse(ph, pw, kmax):
    """Band-limited pulse from a phase array (no DC, no aliasing)."""
    x = np.zeros_like(ph)
    for k in range(1, kmax + 1):
        x += (2.0 / (k * np.pi)) * np.sin(k * np.pi * pw) * np.cos(k * ph)
    return x


def _blsaw(ph, kmax):
    x = np.zeros_like(ph)
    for k in range(1, kmax + 1):
        x -= (2.0 / (k * np.pi)) * np.sin(k * ph)
    return x


def phase(freq, L):
    """Cumulative phase (radians) for a scalar or per-sample frequency."""
    if np.isscalar(freq):
        f = np.full(L, float(freq))
    else:
        f = np.asarray(freq, dtype=np.float64)
        if f.shape[0] != L:
            f = np.interp(np.linspace(0, 1, L), np.linspace(0, 1, f.shape[0]), f)
    return 2 * np.pi * np.cumsum(f) / SR


# ----------------------------------------------------------- non-linearity --

def sat(x, drive=1.0, mix=1.0):
    return x * (1 - mix) + np.tanh(x * drive) * mix


def bitcrush(x, bits=8, hold=1):
    step = 2 ** (bits - 1)
    y = np.round(x * step) / step
    if hold > 1:
        n = len(y) // hold * hold
        y[:n] = np.repeat(y[:n:hold], hold)
    return y


def fold(x, amount=1.0):
    v = x * amount
    for _ in range(3):
        v = np.where(v > 1.0, 2.0 - v, v)
        v = np.where(v < -1.0, -2.0 - v, v)
    return v


# ------------------------------------------------------------------- time ----

def delay(x, ms):
    d = int(ms / 1000 * SR)
    if d <= 0:
        return x
    return np.concatenate([np.zeros(d), x])[:len(x)]


def comp(x, thr=0.10, ratio=3.0, atk=0.005, rel=0.10, mu=1.0):
    e = np.abs(x)
    env_ = _lp(e, 1.0 / max(rel, 1e-3) / 6.283, 1)
    env_ = np.maximum(env_, _lp(e, 1.0 / max(atk, 1e-4) / 6.283, 1) * 0.35)
    g = np.ones_like(x)
    over = env_ > thr
    g[over] = (thr + (env_[over] - thr) / ratio) / (env_[over] + 1e-9)
    return x * g * mu


_IR = {}


def _ir(decay=1.6, seed=7):
    key = (round(decay, 3), seed)
    if key in _IR:
        return _IR[key]
    n = int(decay * SR)
    r = np.random.default_rng(seed)
    e = np.exp(-np.arange(n) / (decay * SR / 4.2))
    irL = r.standard_normal(n) * e
    irR = r.standard_normal(n) * e
    b, a = sg.butter(2, 3600 / (SR / 2), 'low')
    irL = sg.lfilter(b, a, irL)
    irR = sg.lfilter(b, a, irR)
    irR = 0.90 * irR + 0.10 * irL
    pre = int(0.028 * SR)
    irL[:pre] = 0
    irR[:pre] = 0
    irL /= np.abs(irL).sum() / 8
    irR /= np.abs(irR).sum() / 8
    _IR[key] = (irL, irR)
    return _IR[key]


def reverb(l, r, decay=1.6, wet=0.28, seed=7):
    irL, irR = _ir(decay, seed)
    wl = sg.fftconvolve(l, irL)[:len(l)]
    wr = sg.fftconvolve(r, irR)[:len(r)]
    return l * (1 - wet) + wl * wet, r * (1 - wet) + wr * wet


def gated_room(x, decay=2.2, hold_ms=110, wet=0.55):
    """A big room cut off underneath -- huge but still dry-sounding."""
    irL, _ = _ir(decay)
    w = sg.fftconvolve(x, irL)[:len(x)]
    e = _lp(np.abs(x), 18, 2)
    e /= (np.percentile(e, 99.5) + 1e-9)
    g = np.clip(e * 3.2, 0, 1)
    n = int(hold_ms / 1000 * SR)
    if n > 1:
        g = np.minimum(1.0, np.convolve(g, np.ones(n), mode='full')[:len(g)])
    g = _lp(g, 55, 2)
    return x + w * g * wet


def chorus(x, rate=(0.27, 0.41), depth_ms=5.5, base_ms=12.0):
    n = len(x)
    t = np.arange(n) / SR

    def tap(rt, dp, ph):
        d = (base_ms + dp * np.sin(2 * np.pi * rt * t + ph)) / 1000 * SR
        idx = np.clip(np.arange(n) - d, 0, n - 1)
        i0 = idx.astype(int)
        fr = idx - i0
        return x[i0] * (1 - fr) + x[np.minimum(i0 + 1, n - 1)] * fr

    l = 0.72 * x + 0.5 * tap(rate[0], depth_ms, 0.0) + 0.3 * tap(rate[1], depth_ms * 0.55, 1.1)
    r = 0.72 * x + 0.5 * tap(rate[0] * 1.15, depth_ms, 2.3) + 0.3 * tap(rate[1] * 0.9, depth_ms * 0.55, 3.9)
    return l, r


def leslie(x, rate=6.6, depth=0.35, seed=0):
    """Rotary speaker: amplitude + doppler + a little horn/drum split."""
    n = len(x)
    t = np.arange(n) / SR
    ph = 2 * np.pi * rate * t
    horn = _hp(x, 800, 2)
    drum = _lp(x, 800, 2)
    dop = (1.2 + 1.0 * np.sin(ph)) / 1000 * SR
    idx = np.clip(np.arange(n) - dop, 0, n - 1)
    i0 = idx.astype(int)
    fr = idx - i0
    horn = horn[i0] * (1 - fr) + horn[np.minimum(i0 + 1, n - 1)] * fr
    aH = 1 + depth * np.sin(ph)
    aD = 1 + depth * 0.4 * np.sin(ph * 0.82 + 1.1)
    l = horn * aH + drum * aD
    r = horn * (2 - aH) + drum * (2 - aD)
    return l * 0.6, r * 0.6


def tape_wobble(x, wow_rate=0.55, wow_cents=6.0, flutter_rate=7.3,
                flutter_cents=2.0, seed=0):
    n = len(x)
    t = np.arange(n) / SR
    R = np.random.default_rng(seed)
    base = int(0.012 * SR)
    m = (np.sin(2 * np.pi * wow_rate * t + R.uniform(0, 6)) * (wow_cents / 12.0)
         + np.sin(2 * np.pi * flutter_rate * t + R.uniform(0, 6)) * (flutter_cents / 12.0))
    dly = base + m * base * 0.5 * 0.35
    idx = np.clip(np.arange(n) - dly, 0, n - 1)
    i0 = idx.astype(int)
    fr = idx - i0
    return x[i0] * (1 - fr) + x[np.minimum(i0 + 1, n - 1)] * fr


def rms(x):
    return float(np.sqrt(np.mean(x * x) + 1e-18))
