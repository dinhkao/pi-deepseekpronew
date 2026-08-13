"""fretless — bass khong phim

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `fretless`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _bp, _hp, _lp, _peak
from .._core import hz, nn, put


def fretless(b_, t0, m, dur, g=0.30, gl=0.0, vib=1.0, growl=0.30):
    """Fretless: no fret buzz, a slower attack, and vibrato you can hear.

    Same rule as `natbass` -- the note lasts exactly as long as it is written,
    and there is real midrange in it or nobody will hear the melody.
    """
    m = nn(m)
    dur = max(float(dur), 0.06)
    rel = min(0.13, dur * 0.40 + 0.03)
    L = int((min(dur, 3.0) + rel) * SR)
    t = np.arange(L) / SR
    R = np.random.default_rng(3300 + m)
    f0 = hz(m)
    v = 1 + 0.006 * vib * np.sin(2 * np.pi * 5.1 * t + R.uniform(0, 6)) * np.clip((t - 0.18) * 3, 0, 1)
    if gl:
        v *= 2 ** ((gl * np.exp(-t / 0.06)) / 12)
    ph = 2 * np.pi * np.cumsum(f0 * v) / SR
    nP = int(np.clip((SR / 2.4) // max(f0, 1), 4, 26))
    x = np.zeros(L)
    for k in range(1, nP + 1):
        x += (1.0 / (k ** 1.12)) * np.exp(-t / (2.2 / k ** 0.55)) * np.sin(ph * k + R.uniform(0, 6))
    x /= 1.7
    x = _peak(x, 700, 2.0, 0.30)
    body = _lp(x, 2600, 2) * np.minimum(1, t / 0.012)
    y = np.tanh((_lp(body, 240, 2) * 0.8 + body * 0.6
                 + np.tanh(_bp(body, 450, 2600, 2) * 4.0) * growl) * 1.15)
    y = _hp(y, 38, 2)
    rn = int(rel * SR)
    if 0 < rn < L:
        y[-rn:] *= np.linspace(1, 0, rn) ** 1.25
    put(b_, t0, y, g)
