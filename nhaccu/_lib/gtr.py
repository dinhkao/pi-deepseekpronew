"""Helper dung chung, trich tu geeselib/gtr.py.

Trich nguyen van tu `geeselib/gtr.py` cua geese-3d-country.
Chua: `_T`, `_cab4x12`, `gtr_amp`, `spring`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from scipy import signal as sg
from .._dsp import SR, _bp, _hp, _lp, _peak


# Chuan hoa muc ra — muc 5.4 cua KIEM-TRA.
# Do lan dau: fuzz ra RMS 5.33 o gain=1.0 trong khi clav ra 0.032. Chenh 294 lan.
# "Neu cac nguon am co muc ra chenh nhau hon 10 lan thi moi con so gain viet tay
#  deu vo nghia va khong ai doc duoc ban mix." Bang duoi dua tat ca ve ~0.12,
#  cung tam voi nhac cu san co cua greeplib, nen `g=0.10` nghia la nhu nhau
#  o moi nhac cu. Sinh lai bang: python3 tools/calibrate.py
_T = {'fuzz': 0.0225, 'octafuzz': 0.0238, 'wall': 0.0129, 'tremgtr': 0.1124,
      'slidegtr': 0.105, 'pedalsteel': 0.124, 'twelve': 0.1465,
      'baritone': 0.0256, 'ebow': 0.0178}


def _cab4x12(x, bright=1.0, size=1.0):
    """Thung 4x12 dong sau. Ba cong huong + doc rat manh tren 4.5 kHz.

    Day la ly do guitar meo khong bao gio co dai `air`: khong phai do EQ mix,
    ma do CAI LOA. Bo khau nay di thi tieng nghe nhu fuzz pedal cam thang vao
    card am thanh — chinh la loi hay gap nhat khi tong hop guitar bang code.
    """
    y = _peak(x, 105 / size, 1.1, 5.0)
    y = _peak(y, 420 / size, 1.5, -3.0)
    y = _peak(y, 900 * bright, 0.9, 3.5)     # than dan — cho no o 500-2k
    y = _peak(y, 1900 * bright, 1.1, 2.0)
    # Do lan dau tren bai 01: stem guitar co presence(2-4k) = 31%, trong khi
    # bang tham chieu chi cho 2.6-17%. Loa 12 inch that lan dau doc rat manh o
    # day; mo phong nhe tay thi ra tieng "fuzz cam thang vao card am thanh".
    y = _peak(y, 3000 * bright, 1.4, -9.0)
    y = _lp(y, 4000 * bright, 4)
    y = _hp(y, 95, 2)
    return y


def gtr_amp(x, drive=8.0, tone=0.5, bright=1.0, sag=0.35, bias=0.10, size=1.0):
    """Ba tang den + tone stack + thung loa. `sag` = nguon dien sut khi bi dam."""
    y = _hp(x, 70, 2)
    y = np.tanh(y * drive * 0.55 + bias)                 # tang 1, bat doi xung
    y = _peak(y, 700, 0.9, -3.0)
    y = np.tanh(y * drive * 0.45)                        # tang 2
    if sag > 0:
        e = _lp(np.abs(y), 9, 2)
        e /= (np.percentile(e, 99) + 1e-9)
        y = y * (1.0 - sag * 0.45 * np.clip(e, 0, 1))    # nguon sut
    y = np.tanh(y * (1.0 + drive * 0.08))                # tang cong suat
    # tone stack Fender-ish
    y = y + _bp(y, 90, 320, 2) * (0.5 - 0.4 * tone) + _bp(y, 1400, 3600, 2) * (0.25 + 0.6 * tone)
    return _cab4x12(y, bright, size)


def spring(x, wet=0.28, n=3, decay=1.5, seed=3):
    """Lo xo hoi trong ampli: vai duong tre ngan + tan sac (dispersion)."""
    R = np.random.default_rng(seed)
    y = np.zeros_like(x)
    src = _bp(x, 400, 4200, 2)
    for k in range(n):
        d = int((0.024 + 0.011 * k) * SR)
        s = np.concatenate([np.zeros(d), src])[:len(x)]
        for rep in range(1, 7):
            g = decay ** -rep * (0.72 ** k)
            dd = d * rep + int(R.uniform(0, 90))
            if dd < len(x):
                y[dd:] += s[:len(x) - dd] * g * 0.5
    # tan sac: allpass chuoi lam "boing"
    for c in (0.62, -0.55, 0.48):
        y = sg.lfilter([c, 1.0], [1.0, c], y)
    y = _bp(y, 500, 3800, 2)
    return x + y * wet
