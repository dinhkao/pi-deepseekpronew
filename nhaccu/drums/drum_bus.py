"""drum_bus — bus trong

Trich nguyen van tu `greeplib/drums.py` cua geese-3d-country.
Chua: `drum_bus`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import _hp, bitcrush, comp, gated_room


def drum_bus(d, drive=4.0, gate_decay=1.9, gate_wet=0.34, hold_ms=95, crushbits=0):
    """Compress, parallel-distort, then a big room cut off underneath."""
    d = d / (np.abs(d).max() + 1e-9)
    d = comp(d, thr=0.14, ratio=3.4, atk=0.003, rel=0.090) * 0.70
    par = _hp(np.tanh(d * drive), 165, 2) * 0.34
    y = d + par
    if crushbits:
        y = 0.72 * y + 0.28 * bitcrush(y, crushbits, 1)
    return gated_room(y, decay=gate_decay, hold_ms=hold_ms, wet=gate_wet)
