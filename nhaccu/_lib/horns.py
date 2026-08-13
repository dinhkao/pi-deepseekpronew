"""Helper dung chung, trich tu greeplib/horns.py.

Trich nguyen van tu `greeplib/horns.py` cua geese-3d-country.
Chua: `VOICES`, `ODD_ONLY`, `QUARTET`, `BRASS4`, `REEDS`, `SALVATION`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np


# name: (harmonics, tilt, bright_lo, bright_hi, formants[(f,q,g)], noise,
#         attack, scoop_semi, vib_rate, vib_depth, lo_cut, hi_cut)
VOICES = {
    'trumpet':   (26, 0.72, 0.40, 0.93, [(1150, 2.2, 0.55), (2400, 2.6, 0.35)],
                  0.030, 0.022, -0.35, 5.6, 0.0040, 180, 9000),
    'cornet':    (22, 0.80, 0.38, 0.86, [(950, 2.0, 0.50), (2000, 2.4, 0.25)],
                  0.034, 0.028, -0.30, 5.4, 0.0042, 160, 7500),
    'mutedtpt':  (30, 0.62, 0.55, 0.97, [(2100, 4.5, 0.90), (3400, 4.0, 0.55), (900, 3.0, -0.35)],
                  0.055, 0.018, -0.40, 6.2, 0.0050, 400, 10000),
    'trombone':  (30, 0.80, 0.32, 0.90, [(620, 2.0, 0.55), (1300, 2.4, 0.30)],
                  0.028, 0.030, -0.45, 5.0, 0.0038, 90, 7000),
    'basstbn':   (32, 0.86, 0.28, 0.84, [(420, 2.0, 0.55), (900, 2.2, 0.28)],
                  0.026, 0.038, -0.50, 4.6, 0.0034, 60, 5500),
    'tuba':      (30, 0.90, 0.22, 0.72, [(280, 1.8, 0.60), (620, 2.0, 0.25)],
                  0.030, 0.055, -0.55, 4.2, 0.0030, 40, 3800),
    'altosax':   (24, 0.74, 0.42, 0.90, [(830, 2.2, 0.55), (1600, 2.4, 0.42), (2700, 2.6, 0.22)],
                  0.075, 0.024, -0.25, 5.8, 0.0055, 180, 9000),
    'tenorsax':  (26, 0.78, 0.38, 0.88, [(620, 2.0, 0.58), (1250, 2.4, 0.45), (2100, 2.6, 0.22)],
                  0.085, 0.026, -0.30, 5.4, 0.0055, 110, 8000),
    'barisax':   (28, 0.84, 0.32, 0.84, [(420, 2.0, 0.58), (900, 2.2, 0.42), (1700, 2.4, 0.20)],
                  0.090, 0.032, -0.35, 4.8, 0.0048, 60, 6500),
    'oboe':      (22, 0.62, 0.55, 0.92, [(1400, 3.2, 0.75), (2900, 3.0, 0.40), (600, 2.4, -0.30)],
                  0.045, 0.026, -0.20, 5.9, 0.0060, 250, 9000),
    'clarinet':  (24, 0.70, 0.35, 0.82, [(1500, 2.6, 0.45), (3000, 2.6, 0.20)],
                  0.040, 0.030, -0.18, 5.2, 0.0040, 140, 8000),
    'flute':     (10, 0.45, 0.30, 0.62, [(800, 1.6, 0.30), (2200, 1.8, 0.18)],
                  0.320, 0.030, -0.15, 5.6, 0.0060, 260, 11000),
    'frenchhorn': (28, 0.86, 0.26, 0.78, [(480, 1.8, 0.55), (1100, 2.2, 0.30)],
                  0.038, 0.048, -0.40, 4.8, 0.0038, 90, 5000),
}


# Clarinets and (to a lesser degree) flutes suppress even harmonics.
ODD_ONLY = {'clarinet': 0.30, 'flute': 0.55, 'oboe': 0.80}


QUARTET = ['trumpet', 'altosax', 'trombone', 'barisax']


BRASS4 = ['trumpet', 'trumpet', 'trombone', 'basstbn']


REEDS = ['oboe', 'altosax', 'tenorsax', 'barisax']


SALVATION = ['cornet', 'cornet', 'trombone', 'tuba']   # brass-band colours
