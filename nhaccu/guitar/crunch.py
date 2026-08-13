"""crunch — guitar rhythm meo vua

Trich nguyen van tu `greeplib/inst.py` cua geese-3d-country.
Chua: `_cab`, `crunch`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from scipy import signal as sg
from .._dsp import SR, _bp, _fadeout, _hp, _lp, _peak, _ramp, env
from .._core import nn, put
from .._lib.inst import ks


def _cab(x, bright=1.0):
    y = _bp(x, 82, 5400, 2)
    y = _peak(y, 110, 2.2, 0.55)
    y = _peak(y, 2100, 2.6, 0.40 * bright)
    bq, aq = sg.iirnotch(880 / (SR / 2), 3.0)
    return _lp(sg.lfilter(bq, aq, y), 6200, 4)


def crunch(b_, t0, notes, dur, g=0.10, drive=9.0, seed=0, spread=0.006, bright=1.0):
    """Distorted chord/stack -- distortion first, then the cabinet."""
    ns = np.atleast_1d(notes)
    L = int(min(dur + 0.35, 3.0) * SR)
    mix = np.zeros(L)
    for j, m in enumerate(ns):
        x = ks(int(nn(m)), min(dur + 0.35, 3.0), 0.9975, 0.42, seed + j * 5).astype(np.float64)
        d = int(j * spread * SR)
        n = min(len(x), L - d)
        if n > 0:
            mix[d:d + n] += x[:n]
    t = np.arange(L) / SR
    mix *= (1 - 0.18 * (1 - np.exp(-t / 0.35)))
    y = np.tanh(mix * drive) + np.tanh(_hp(mix, 420, 2) * drive * 1.8) * 0.35
    y = _cab(y, bright)
    y *= env(L, 0.004, 0.12, 0.80, min(0.20, dur * 0.45 + 0.04))
    put(b_, t0, _fadeout(_ramp(y, 0.7), 20.0), g * 0.55)
