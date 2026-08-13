"""pedalsteel — pedal steel

Trich nguyen van tu `geeselib/gtr.py` cua geese-3d-country.
Chua: `pedalsteel`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _fadeout, _lp, _peak, _ramp
from .._core import nn, put
from .._lib.gtr import _T, spring
from .._lib.inst import damp, ks


def pedalsteel(b_, t0, notes, dur, g=0.09, seed=0, bend=(0, 2, 0), spread=0.012):
    """Pedal steel: hop am ma MOT VAI day bi keo len, cac day khac dung yen.

    `bend` la so nua cung keo cho tung not (dung 0 de giu). Day la thu tao ra
    tieng "khoc" cua country — khong phai reverb, ma la hai cao do di lech nhau
    roi gap lai.
    """
    R = np.random.default_rng(seed + 55)
    for i, m in enumerate(sorted(nn(x) for x in notes)):
        bs = bend[i % len(bend)]
        x = ks(m, dur + 0.6, damp=0.9982, bright=0.42, seed=seed + i * 11)
        L = int((dur + 0.3) * SR)
        t = np.arange(L) / SR
        if bs:
            p = np.clip(t / max(dur * 0.45, 1e-3), 0, 1)
            p = p * p * (3 - 2 * p)
            ratio = 2 ** (bs * p / 12.0)
        else:
            ratio = np.ones(L)
        ratio *= 2 ** (float(R.normal(0, 5)) / 1200.0)
        pos = np.clip(np.cumsum(ratio), 0, len(x) - 2)
        i0 = pos.astype(int)
        fr = pos - i0
        y = x[i0] * (1 - fr) + x[i0 + 1] * fr
        y = damp(y, dur, ring=dur * 0.95, rel=0.09)
        y = _peak(y, 1500, 1.0, 4.0)
        y = _lp(np.tanh(y * 2.4), 5200, 3)
        y = spring(y, wet=0.34)
        put(b_, t0 + i * spread, _fadeout(_ramp(y, 3.0), 45.0), g * _T['pedalsteel'])
