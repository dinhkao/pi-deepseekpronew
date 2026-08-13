"""Helper dung chung, trich tu geeselib/voice.py.

Trich nguyen van tu `geeselib/voice.py` cua geese-3d-country.
Chua: `_snap_all`, `LEAD_DEFAULTS`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._harmony import snap


def _snap_all(base, pcs, offsets, lo=40, hi=84):
    """Bien danh sach quang GOI Y thanh not hop am that."""
    out = []
    for iv in offsets:
        m = snap(base + iv, pcs, direction=0, lo=lo, hi=hi)
        while m in out:
            m = snap(m + 1, pcs, direction=1, lo=lo, hi=hi)
        out.append(m)
    return out


# Do duoc bang cach cho Whisper nghe giong tach rieng (PHAN-TICH muc 19):
#   giong THAT cua dia tham chieu  -> chep ra sach, cau nao ra cau do
#   giong tong hop, vib = 24 cent  -> khong ra gi ("A-N-E-M-I-A-N")
#   giong tong hop, vib =  4 cent  -> ra duoc hinh dang cau, phan lon tu chuc nang
# Rung sau lam nhoe formant: F1/F2 la cai tai dung de nhan ra NGUYEN AM, ma
# rung 24 cent keo chung di qua lai lien tuc. Ca si that rung bang thanh quan
# nhung formant do KHOANG MIENG quyet dinh va khoang mieng thi dung yen — mo
# hinh nguon-bo loc o day khong tach duoc hai thu do, nen phai giu rung nho.
#
# Ket luan da kiem chung duoc: rung nho + phu am dai hon = nghe ra chu hon.
# Do CHUA bang giong that; xem README, muc "gioi han".
LEAD_DEFAULTS = dict(vib=6.0, cons=1.45, cgain=1.45)
