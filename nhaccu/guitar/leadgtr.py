"""leadgtr — guitar lead co drive

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `leadgtr`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from scipy import signal as sg
from .._dsp import SR, _bp, _fadeout, env
from .._core import put
from .._lib.inst import damp, ks


def leadgtr(b_, t0, m, dur, g=0.13, bend=0.0, drive=9.0, seed=0, wah=0.0,
            ring=None):
    """Overdriven single-note lead. `bend` in semitones, applied on attack."""
    x = ks(m, dur, 0.9975, 0.65, seed).astype(np.float64)
    x = np.tanh(x * drive)
    L = len(x)
    if bend:
        t = np.arange(L) / SR
        d = (2 ** ((bend * np.minimum(1, t * 6)) / 12) - 1)
        idx = np.clip(np.cumsum(1 + d), 0, L - 1)
        i0 = idx.astype(int)
        fr = idx - i0
        x = x[i0] * (1 - fr) + x[np.minimum(i0 + 1, L - 1)] * fr
    x = _bp(x, 150, 4600, 2)
    if wah:
        t = np.arange(L) / SR
        out = np.zeros(L)
        step = 1024
        for i in range(0, L, step):
            fc = float(np.clip(600 + 1400 * (0.5 + 0.5 * np.sin(2 * np.pi * wah * t[min(i, L - 1)])), 300, 4000))
            bq, aq = sg.iirpeak(fc / (SR / 2), 4.0)
            seg = sg.lfilter(bq, aq, x[i:i + step * 2])[:min(step, L - i)]
            out[i:i + len(seg)] += seg
        x = x * 0.4 + out * 0.9
    put(b_, t0, damp(_fadeout(x * env(L, 0.004, 0.10, 0.90, 0.15), 25.0),
                     dur, ring), g)
