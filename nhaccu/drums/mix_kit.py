"""mix_kit — mix bo trong

Trich nguyen van tu `greeplib/drums.py` cua geese-3d-country.
Chua: `mix_kit`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import _bp, _hp, _lp, delay


def mix_kit(bus, room=0.22, oh=0.85, lpf=10500, lperc_gain=1.0):
    """Sum the kit buses through bleed, overheads and a room mic."""
    K, S, H, TMb, CY, PC, LP = (bus['kick'], bus['snare'], bus['hat'], bus['tom'],
                                bus['cym'], bus['perc'], bus['lperc'])
    kick_m = K + _lp(delay(S, 0.6), 800) * 0.11 + _lp(delay(TMb, 0.8), 700) * 0.09
    snare_m = S + _lp(delay(K, 0.5), 650) * 0.15 + _hp(delay(H, 0.3), 1500) * 0.17 + delay(TMb, 0.7) * 0.12
    hat_m = _hp(H, 400) + _hp(delay(S, 0.4), 900) * 0.20
    tom_m = TMb + _lp(delay(K, 0.6), 600) * 0.10 + delay(S, 0.5) * 0.14
    ohsrc = _lp(K, 900) * 0.42 + S * 0.85 + H * 0.95 + TMb * 0.75 + CY * 1.0 + PC * 0.6 + LP * 0.8
    OH = _hp(delay(ohsrc, 3.8), 120)
    rsrc = _lp(K, 1200) * 0.6 + S + H * 0.7 + TMb + CY * 0.9 + PC * 0.7 + LP * 0.9
    RM = delay(rsrc, 8.7)
    for d, g in [(17, 0.5), (23, 0.38), (31, 0.3), (41, 0.22), (53, 0.16)]:
        RM = RM + delay(rsrc, 8.7 + d) * g
    RM = _bp(np.tanh(RM * 1.5), 180, 7000, 2)
    dry = (kick_m * 1.0 + snare_m * 0.95 + hat_m * 0.55 + tom_m * 0.8
           + CY * 0.5 + PC * 0.85 + LP * lperc_gain)
    return _lp(dry + OH * oh + RM * room, lpf, 3)
