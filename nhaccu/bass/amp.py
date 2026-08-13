"""amp — ampli bass

Trich nguyen van tu `greeplib/bassgtr.py` cua geese-3d-country.
Chua: `amp`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import _bp, _hp, _lp, _peak, comp


def amp(x, drive=1.6, tone=0.5, cab=True, comp_amt=0.5, di=0.25):
    """One amp, applied to the whole bass part -- not per note.

    Chain: a little compression, a tube-ish asymmetric clip (which is where
    the even harmonics that make a bass sound 'warm' actually come from), the
    speaker cabinet, and a blend of the clean DI underneath so the bottom
    octave stays tight.
    """
    dry = x.copy()
    y = x
    if comp_amt > 0:
        y = comp(y, thr=0.16, ratio=2.6 + 2.0 * comp_amt, atk=0.008,
                 rel=0.120, mu=1.0 + 0.35 * comp_amt)
    # preamp EQ: a lift at the bottom and a scoop where mud lives
    y = _peak(y, 80, 1.1, 0.28)
    y = y - _bp(y, 300, 620, 2) * 0.22
    y = _peak(y, 780 + 900 * tone, 1.3, 0.30 + 0.30 * tone)
    # asymmetric soft clip: positive half harder than negative
    d = y * drive
    y = np.where(d >= 0, np.tanh(d), np.tanh(d * 0.78) * 1.12) / max(drive, 1e-6)
    if cab:
        # 15" driver: resonance low down, breakup in the mids, gone by 4 kHz
        y = _peak(y, 74, 1.6, 0.45)
        y = _peak(y, 1450, 1.2, 0.22)
        y = _bp(y, 38, 4200, 2)
        y = y - _bp(y, 2600, 3600, 2) * 0.30
    # the engineer always keeps some DI under the amp
    out = y * (1 - di) + _lp(dry, 900, 2) * di * 1.25
    return _hp(out, 34, 2)
