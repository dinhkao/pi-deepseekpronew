"""g2p — chu -> am vi

Trich nguyen van tu `greeplib/singer.py` cua geese-3d-country.
Chua: `_DIGRAPH`, `_SINGLE`, `_VOWELS`, `g2p`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np
from .._lib.singer import LEX


_DIGRAPH = [
    ('tion', 'sh-@-n'), ('sion', 'zh-@-n'), ('ough', 'V-f'), ('augh', 'A-f'),
    ('eigh', 'eI'), ('igh', 'aI'), ('ing', 'I-ng'), ('ck', 'k'), ('ch', 'ch'),
    ('sh', 'sh'), ('th', 'th'), ('ph', 'f'), ('wh', 'w'), ('qu', 'k-w'),
    ('ng', 'ng'), ('ai', 'eI'), ('ay', 'eI'), ('ea', 'i'), ('ee', 'i'),
    ('ie', 'i'), ('oa', 'oU'), ('oe', 'oU'), ('oo', 'u'), ('ou', 'aU'),
    ('ow', 'aU'), ('oi', 'OI'), ('oy', 'OI'), ('au', 'O'), ('aw', 'O'),
    ('ew', 'yu'), ('ue', 'u'), ('ui', 'u'), ('ar', 'a-r'), ('er', 'R'),
    ('ir', 'R'), ('ur', 'R'), ('or', 'O-r'),
]


_SINGLE = {'a': 'A', 'e': 'E', 'i': 'I', 'o': 'O', 'u': 'V', 'y': 'i',
           'b': 'b', 'c': 'k', 'd': 'd', 'f': 'f', 'g': 'g', 'h': 'h',
           'j': 'j', 'k': 'k', 'l': 'l', 'm': 'm', 'n': 'n', 'p': 'p',
           'q': 'k', 'r': 'r', 's': 's', 't': 't', 'v': 'v', 'w': 'w',
           'x': 'k-s', 'z': 'z'}


_VOWELS = set('aeiouy')


def g2p(word):
    """Very rough English letter-to-sound. Good enough for a syllable that
    isn't in LEX; anything important should be in LEX."""
    w = ''.join(c for c in word.lower() if c.isalpha())
    if not w:
        return '@'
    if w in LEX:
        return LEX[w]
    # collapse doubled consonants: 'hello' is not 'hel-lo'
    out_w = [w[0]]
    for c in w[1:]:
        if c == out_w[-1] and c not in _VOWELS:
            continue
        out_w.append(c)
    w = ''.join(out_w)
    # a word-final 'o' or 'y' is long
    if w.endswith('o'):
        w = w[:-1] + '\x01'
    elif len(w) > 2 and w.endswith('y'):
        w = w[:-1] + '\x02'
    # magic e: 'ride' -> long vowel, drop the e
    magic = (len(w) >= 3 and w[-1] == 'e' and w[-2] not in _VOWELS
             and any(c in _VOWELS for c in w[:-2]))
    if magic:
        w = w[:-1]
    out = []
    i = 0
    while i < len(w):
        for pat, rep in _DIGRAPH:
            if w.startswith(pat, i):
                out.append(rep)
                i += len(pat)
                break
        else:
            c = w[i]
            if c == 'c' and i + 1 < len(w) and w[i + 1] in 'eiy':
                out.append('s')
            elif c == 'g' and i + 1 < len(w) and w[i + 1] in 'eiy':
                out.append('j')
            elif c == 's' and 0 < i and i == len(w) - 1 and w[i - 1] in 'bdglmnrvwz' + ''.join(_VOWELS):
                out.append('z')
            elif c == '\x01':
                out.append('oU')
            elif c == '\x02':
                out.append('i')
            elif c in _SINGLE:
                out.append(_SINGLE[c])
            i += 1
    if magic and out:
        # promote the last vowel to its long form
        longs = {'A': 'eI', 'E': 'i', 'I': 'aI', 'O': 'oU', 'V': 'yu'}
        for k in range(len(out) - 1, -1, -1):
            if out[k] in longs:
                out[k] = longs[out[k]]
                break
    return '-'.join(out) or '@'
