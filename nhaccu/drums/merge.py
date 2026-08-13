"""merge — ghep mau nhip

Trich nguyen van tu `greeplib/drums.py` cua geese-3d-country.
Chua: `merge`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np


def merge(*pats):
    """Overlay step-strings; later non-'.' characters win."""
    out = {}
    for p in pats:
        for k, v in p.items():
            if k not in out:
                out[k] = v
            else:
                a, b = out[k], v
                m = max(len(a), len(b))
                a = a.ljust(m, '.')
                b = b.ljust(m, '.')
                out[k] = ''.join(y if y != '.' else x for x, y in zip(a, b))
    return out
