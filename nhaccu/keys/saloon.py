"""saloon — piano quan ruou (lac day)

Trich nguyen van tu `geeselib/keys.py` cua geese-3d-country.
Chua: `_TUNE_TRIM`, `saloon`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._dsp import SR, _bp, _fadeout, _peak, _ramp
from .._core import nn, put
from .._lib.inst import _piano_raw, damp
from .._lib.keys import _T


# Bang 0 la co y. Ban dau dat 10.0 vi autocorrelation bao piano lech +30..+44
# cent. Do lai bang DINH FFT o tan so co ban thi ra +0.6..+6.1 cent — tuc mo
# hinh piano von da dung, con autocorrelation thi bi boi am khong dieu hoa cua
# piano danh lua. KIEM-TRA muc 0.2: "neu mot phep do cho ket qua nghe co ve vo
# ly, nghi ngo phep do truoc, nghi ngo bai nhac sau."
_TUNE_TRIM = 0.0


def saloon(b_, t0, m, dur=None, g=0.10, ring=2.2, detune=16.0, seed=0):
    """Piano quan ruou: day lech nhau nhieu, bua cung, mat het cuc tram va cuc cao.

    Lech cu duoc lam bang doc lai mau — re hon tong hop lai va van dung.
    """
    x = _piano_raw(nn(m))
    R = np.random.default_rng(seed + int(nn(m)) * 13)
    # `_TUNE_TRIM` bu do lech he thong cua chinh mo hinh piano (do duoc +5..+16
    # cent tren toan dai). Lech cu nghe thuat cua dan quan ruou van giu, nhung
    # bay gio no lech quanh dung cao do chu khong lech quanh mot cao do sai.
    c = 2 ** ((float(R.normal(0, detune)) - _TUNE_TRIM) / 1200.0)
    pos = np.clip(np.arange(len(x)) * c, 0, len(x) - 2)
    i0 = pos.astype(int)
    fr = pos - i0
    y = x[i0] * (1 - fr) + x[i0 + 1] * fr
    # Comb 2.8 ms o ban dau lam cao do do duoc lech toi +44 cent (gan mot phan
    # tu cung) — do tre trong comb cong vao chu ky hieu dung y het co che ma
    # KIEM-TRA muc 3.3 mo ta cho vong lap day. Rut xuong 0.9 ms va giam do sau.
    y = y + np.concatenate([np.zeros(int(0.0009 * SR)), y])[:len(y)] * 0.30
    y = _peak(y, 2600, 1.2, 5.0)
    y = _bp(y, 130, 6000, 2)
    y = damp(y, dur if dur else ring, ring=ring, rel=0.10)
    put(b_, t0, _fadeout(_ramp(y, 1.5), 30.0), g * _T['saloon'])
