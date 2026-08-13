"""Helper dung chung, trich tu greeplib/inst.py.

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `_KS`, `damp`, `ks`, `_PN`, `_piano_raw`, `LVL`, `GAIN`, `lvl`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from scipy import signal as sg
from .._dsp import SR, _bp, _fadeout, _lp, _ramp
from .._core import hz, nn


_KS = {}


def damp(y, dur, ring=None, rel=None):
    """Stop a plucked note when it was written to stop.

    Every instrument in here builds a string and then lets it ring for a fixed
    extra time -- which is physically true of a string and musically wrong,
    because a player's hand is part of the instrument. On anything that changes
    chord often, a note still sounding into the next bar is heard as being out
    of tune, not as being resonant.

    `ring` overrides, for the places where a long tail is actually wanted.
    """
    ring = dur if ring is None else ring
    rel = min(0.09, ring * 0.30 + 0.02) if rel is None else rel
    n = int((min(ring, 6.0) + rel) * SR)
    if len(y) > n:
        y = y[:n]
    rn = int(rel * SR)
    if 0 < rn < len(y):
        y = y.copy()
        y[-rn:] *= np.linspace(1, 0, rn) ** 1.3
    return y


def ks(m, dur, damp=0.9955, bright=0.55, seed=0):
    """Karplus-Strong via an IIR comb with fractional delay.

    The excitation is a filtered noise burst PLUS a raised half-sine of
    exactly one period: without that, the energy at f0 varies wildly from
    semitone to semitone and the instrument sounds out of tune with itself.
    """
    m = nn(m)
    key = (m, round(dur, 2), round(bright, 2), round(damp, 4), seed)
    if key in _KS:
        return _KS[key]
    f = hz(m)
    D = SR / f
    N = max(int(np.floor(D)), 2)
    fr = float(np.clip(D - N, 0.0, 1.0))
    L = int(dur * SR) + int(0.15 * SR)
    r2 = np.random.default_rng(1000 + int(m) * 7 + seed)
    burst = r2.standard_normal(N)
    b, a = sg.butter(2, min(900 + 7000 * bright, SR / 2 - 200) / (SR / 2), 'low')
    burst = sg.lfilter(b, a, burst)
    burst *= np.linspace(1, 0.2, N)
    burst /= (np.abs(burst).max() + 1e-9)
    burst = 0.55 * burst + 0.85 * np.sin(np.pi * np.arange(N) / N)
    exc = np.zeros(L)
    exc[:N] = burst
    A = np.zeros(N + 2)
    A[0] = 1.0
    A[N] = -damp * (1.0 - fr)
    A[N + 1] = -damp * fr
    y = sg.lfilter([1.0], A, exc)
    y *= np.exp(-np.arange(L) / SR * 0.55)
    y /= (np.abs(y).max() + 1e-9)
    _KS[key] = _fadeout(_ramp(y, 0.8), 20.0).astype(np.float32)
    return _KS[key]


_PN = {}


def _piano_raw(m):
    if m in _PN:
        return _PN[m]
    f0 = hz(m)
    ring = float(np.clip(2.0 + (84 - m) * 0.095, 1.6, 7.0))
    L = int(ring * SR)
    t = np.arange(L) / SR
    B = 0.00035 * (2.0 ** ((58 - m) / 22.0))
    nP = int(np.clip((SR / 2.4) // max(f0, 1), 2, 26))
    R = np.random.default_rng(300 + m)
    out = np.zeros(L)
    for k in range(1, nP + 1):
        fk = f0 * k * np.sqrt(1.0 + B * k * k)
        if fk > SR / 2.2:
            break
        tau_f = 0.28 / (k ** 0.80)
        tau_s = (ring * 0.70) / (k ** 0.42)
        amp = (1.0 / (k ** 1.22)) * (0.72 if k % 2 == 0 else 1.0)
        e = 0.52 * np.exp(-t / tau_f) + 0.48 * np.exp(-t / tau_s)
        s = np.zeros(L)
        for d in (-1.1, 0.0, 1.4):
            s += np.sin(2 * np.pi * fk * (2 ** (d / 1200.0)) * t + R.uniform(0, 2 * np.pi))
        out += amp * e * (s / 3.0)
    ham = _bp(R.standard_normal(L), 900, 5200, 2) * np.exp(-t / 0.0032) * 0.34
    thud = _lp(R.standard_normal(L), 260, 2) * np.exp(-t / 0.010) * 0.28
    out = out / (np.abs(out).max() + 1e-9) + ham + thud
    out *= np.minimum(1.0, t * 2600)
    _PN[m] = out.astype(np.float32)
    return _PN[m]


# =============================================== level normalisation table ===
# Raw output levels differ by more than 10x across these instruments, which
# makes writing a balance by hand impossible.  These factors were MEASURED
# (1.0 s note, RMS over 2.2 s) and normalise everything to "RMS 0.05 at g=1.0",
# so `g=LVL['nylon'] * 0.8` means the same loudness as `g=LVL['rhodes'] * 0.8`.
LVL = {
    'accordion': 1.066, 'acgtr': 0.813, 'bell': 0.127, 'clav': 1.188,
    'crunch': 0.624, 'fretless': 0.121, 'glass': 0.185, 'harmonium': 0.809,
    'jangle': 0.575, 'jazzbox': 0.659, 'leadgtr': 0.336, 'marimba': 0.186,
    'melodica': 0.151, 'natbass': 0.160, 'nylon': 0.862, 'organ': 0.624,
    'pipeorgan': 0.736, 'pizz': 0.339, 'pno': 0.289, 'piano': 0.289,
    'rhodes': 0.109, 'strings': 0.125, 'upright': 0.183, 'vibes': 0.103,
    'voxorgan': 0.627, 'wurli': 0.156,
    # horns (single player) and the 4-part section
    'trumpet': 0.138, 'cornet': 0.137, 'mutedtpt': 0.177, 'trombone': 0.123,
    'basstbn': 0.154, 'tuba': 0.143, 'altosax': 0.137, 'tenorsax': 0.124,
    'barisax': 0.154, 'oboe': 0.147, 'clarinet': 0.146, 'flute': 0.152,
    'frenchhorn': 0.122, 'section': 0.067,
    'sing': 0.211,
}


GAIN = LVL   # older name


def lvl(name, mult=1.0):
    return LVL.get(name, 0.5) * mult
