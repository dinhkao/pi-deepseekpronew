"""strings — dan day (not don)

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `_SD`, `_ST`, `_desk`, `strings`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _bp
from .._core import hz, nn, put


_SD = {}


_ST = {}


def _desk(m, dur, det, seed, atk):
    """One desk of players. Independent intonation walk, independent bow
    changes, independent vibrato -- which is the only reason a stack of these
    sounds like a section rather than a chorus effect."""
    key = (m, round(dur, 1), round(det, 1), seed, round(atk, 2))
    if key in _SD:
        return _SD[key]
    L = int(min(dur, 12.0) * SR) + int(0.55 * SR)
    t = np.arange(L) / SR
    f0 = hz(m)
    R = np.random.default_rng(1700 + m * 13 + seed * 7)
    step = 0.06
    nw = int(L / (SR * step)) + 3
    w = np.cumsum(R.normal(0, 1, nw))
    w -= w.mean()
    w = w / (np.abs(w).max() + 1e-9) * R.uniform(2.0, 5.5)
    walk = np.interp(t, np.arange(nw) * step, w)
    vr = R.uniform(4.1, 6.3)
    vdr = 1 + 0.14 * np.sin(2 * np.pi * R.uniform(0.11, 0.24) * t + R.uniform(0, 6))
    vph = 2 * np.pi * np.cumsum(vr * vdr) / SR
    vd = np.clip((t - R.uniform(0.30, 0.75)) / R.uniform(0.7, 1.4), 0, 1) * R.uniform(0.0035, 0.0075)
    vib = vd * np.sin(vph + R.uniform(0, 6))
    ratio = (2 ** ((det + walk) / 1200.0)) * (1 + vib)
    ph = 2 * np.pi * np.cumsum(f0 * ratio) / SR
    nP = int(np.clip((SR / 2.6) // max(f0, 1), 4, 22))
    body = np.zeros(L)
    for k in range(1, nP + 1):
        if f0 * k > SR / 2.3:
            break
        body += (1.0 / (k ** 1.30)) * np.sin(ph * k + R.uniform(0, 2 * np.pi))
    bowg = np.ones(L)
    bown = np.zeros(L)
    tc = R.uniform(0.9, 1.6)
    while tc < min(dur, 11.5):
        i = int(tc * SR)
        bowg -= R.uniform(0.16, 0.34) * np.exp(-((t - tc) / R.uniform(0.030, 0.055)) ** 2)
        seg = int(0.05 * SR)
        if 0 <= i and i + seg < L:
            bown[i:i + seg] += _bp(R.standard_normal(seg), 1600, 6000, 2) * np.exp(-np.arange(seg) / SR / 0.010)
        tc += R.uniform(1.1, 2.6)
    bowg = np.clip(bowg, 0.35, 1.0)
    a = np.minimum(1, t / max(atk, 0.02)) ** 1.35
    sw = (1 + 0.17 * np.sin(2 * np.pi * R.uniform(0.13, 0.26) * t + R.uniform(0, 6))
          + 0.08 * np.sin(2 * np.pi * R.uniform(0.5, 0.9) * t + R.uniform(0, 6)))
    amp = a * bowg * sw
    rel = int(min(0.55, dur * 0.38) * SR)
    if 0 < rel < L:
        amp[-rel:] *= np.linspace(1, 0, rel) ** 1.25
    x = body * amp + bown * 0.020
    dk = _bp(x, 60, 2400, 2)
    br = _bp(x, 60, 7000, 2)
    d = np.clip(amp / (np.percentile(amp, 95) + 1e-9), 0, 1.4)
    x = dk * (1 - 0.55 * d) + br * (0.42 + 0.58 * d)
    _SD[key] = x.astype(np.float32)
    return _SD[key]


def strings(b_, t0, m, dur, g=0.08, atk=0.22, seed=0, desks=4):
    m = nn(m)
    key = (m, round(dur, 1), round(atk, 2), seed % 4, desks)
    if key not in _ST:
        R = np.random.default_rng(2600 + m * 5 + seed)
        out = None
        for i in range(desks):
            det = float(R.normal(0, 7.5))
            ak = max(0.03, atk * float(1 + R.normal(0, 0.18)))
            d = _desk(m, dur, det, (seed * 11 + i) % 64, ak).astype(np.float64)
            off = int(max(0.0, R.normal(0.013, 0.010)) * SR)
            if out is None:
                out = np.zeros(len(d) + int(0.12 * SR))
            n = min(len(d), len(out) - off)
            out[off:off + n] += d[:n]
        _ST[key] = (out / desks).astype(np.float32)
    put(b_, t0, _ST[key].astype(np.float64), g)
