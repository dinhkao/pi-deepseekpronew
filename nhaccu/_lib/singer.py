"""Helper dung chung, trich tu greeplib/singer.py.

Trich nguyen van tu `greeplib/singer.py` cua geese-3d-country.
Chua: `LEX`

File nay duoc sinh tu dong (tools/extract.py). Sua o repo goc roi tach lai.
"""
from __future__ import annotations

import numpy as np


LEX = {
    # function words
    'a': '@', 'the': 'dh-@', 'thee': 'dh-i', 'and': 'A-n-d', 'an': 'A-n',
    'i': 'aI', 'im': 'aI-m', 'ive': 'aI-v', 'ill': 'aI-l', 'id': 'aI-d',
    'you': 'y-u', 'youre': 'y-O-r', 'youve': 'y-u-v', 'youll': 'y-u-l',
    'your': 'y-O-r', 'my': 'm-aI', 'me': 'm-i', 'we': 'w-i', 'he': 'h-i',
    'she': 'sh-i', 'they': 'dh-eI', 'them': 'dh-E-m', 'their': 'dh-E-r',
    'it': 'I-t', 'its': 'I-t-s', 'is': 'I-z', 'was': 'w-V-z', 'were': 'w-R',
    'be': 'b-i', 'been': 'b-I-n', 'am': 'A-m', 'are': 'a-r', 'aint': 'eI-n-t',
    'to': 't-u', 'too': 't-u', 'two': 't-u', 'of': 'V-v', 'off': 'O-f',
    'in': 'I-n', 'on': 'O-n', 'at': 'A-t', 'by': 'b-aI', 'for': 'f-O-r',
    'with': 'w-I-th', 'from': 'f-r-V-m', 'into': 'I-n-t-u', 'out': 'aU-t',
    'up': 'V-p', 'down': 'd-aU-n', 'over': 'oU-v-R', 'under': 'V-n-d-R',
    'no': 'n-oU', 'not': 'n-O-t', 'nor': 'n-O-r', 'so': 's-oU', 'as': 'A-z',
    'but': 'b-V-t', 'or': 'O-r', 'if': 'I-f', 'that': 'dh-A-t', 'this': 'dh-I-s',
    'there': 'dh-E-r', 'theres': 'dh-E-r-z', 'thats': 'dh-A-t-s', 'then': 'dh-E-n',
    'when': 'w-E-n', 'where': 'w-E-r', 'what': 'w-V-t', 'who': 'h-u',
    'how': 'h-aU', 'why': 'w-aI', 'all': 'O-l', 'one': 'w-V-n', 'once': 'w-V-n-s',
    'now': 'n-aU', 'never': 'n-E-v-R', 'ever': 'E-v-R', 'again': '@-g-E-n',
    'still': 's-t-I-l', 'just': 'j-V-s-t', 'like': 'l-aI-k', 'more': 'm-O-r',
    'every': 'E-v-r-i', 'some': 's-V-m', 'any': 'E-n-i', 'own': 'oU-n',
    'do': 'd-u', 'does': 'd-V-z', 'did': 'd-I-d', 'dont': 'd-oU-n-t',
    'can': 'k-A-n', 'cant': 'k-A-n-t', 'will': 'w-I-l', 'wont': 'w-oU-n-t',
    'would': 'w-U-d', 'could': 'k-U-d', 'should': 'sh-U-d', 'let': 'l-E-t',
    'got': 'g-O-t', 'get': 'g-E-t', 'has': 'h-A-z', 'have': 'h-A-v',
    'had': 'h-A-d', 'said': 's-E-d', 'says': 's-E-z', 'say': 's-eI',
    'go': 'g-oU', 'goes': 'g-oU-z', 'gone': 'g-O-n', 'come': 'k-V-m',
    'came': 'k-eI-m', 'know': 'n-oU', 'knows': 'n-oU-z', 'new': 'n-yu',
    'good': 'g-U-d', 'well': 'w-E-l', 'yes': 'y-E-s', 'oh': 'oU', 'ooh': 'u',
    'ah': 'a', 'ha': 'h-a', 'hey': 'h-eI', 'la': 'l-a', 'na': 'n-a',
    'da': 'd-a', 'ba': 'b-a', 'doo': 'd-u', 'mm': 'm', 'yeah': 'y-A',
    # nouns and verbs the record leans on
    'man': 'm-A-n', 'men': 'm-E-n', 'boy': 'b-OI', 'girl': 'g-R-l',
    'god': 'g-O-d', 'love': 'l-V-v', 'money': 'm-V-n-i', 'mirror': 'm-I-r-R',
    'night': 'n-aI-t', 'light': 'l-aI-t', 'lights': 'l-aI-t-s',
    'floor': 'f-l-O-r', 'door': 'd-O-r', 'room': 'r-u-m', 'house': 'h-aU-s',
    'street': 's-t-r-i-t', 'city': 's-I-t-i', 'town': 't-aU-n',
    'wine': 'w-aI-n', 'drink': 'd-r-I-ng-k', 'smoke': 's-m-oU-k',
    'dance': 'd-A-n-s', 'song': 's-O-ng', 'sing': 's-I-ng', 'band': 'b-A-n-d',
    'name': 'n-eI-m', 'face': 'f-eI-s', 'eyes': 'aI-z', 'hand': 'h-A-n-d',
    'hands': 'h-A-n-d-z', 'heart': 'h-a-r-t', 'head': 'h-E-d',
    'mouth': 'm-aU-th', 'teeth': 't-i-th', 'skin': 's-k-I-n',
    'suit': 's-u-t', 'coat': 'k-oU-t', 'shoes': 'sh-u-z', 'gold': 'g-oU-l-d',
    'king': 'k-I-ng', 'queen': 'k-w-i-n', 'god': 'g-O-d',
    'time': 't-aI-m', 'year': 'y-Ir', 'day': 'd-eI', 'morning': 'm-O-r-n-I-ng',
    'life': 'l-aI-f', 'death': 'd-E-th', 'dead': 'd-E-d', 'blood': 'b-l-V-d',
    'work': 'w-R-k', 'wait': 'w-eI-t', 'walk': 'w-O-k', 'talk': 't-O-k',
    'run': 'r-V-n', 'stand': 's-t-A-n-d', 'sit': 's-I-t', 'fall': 'f-O-l',
    'sea': 's-i', 'sun': 's-V-n', 'moon': 'm-u-n', 'rain': 'r-eI-n',
    'fire': 'f-aI-R', 'water': 'w-O-t-R', 'wind': 'w-I-n-d',
    'best': 'b-E-s-t', 'worst': 'w-R-s-t', 'first': 'f-R-s-t', 'last': 'l-A-s-t',
    'big': 'b-I-g', 'small': 's-m-O-l', 'long': 'l-O-ng', 'true': 't-r-u',
    'real': 'r-i-l', 'fine': 'f-aI-n', 'nice': 'n-aI-s', 'rich': 'r-I-ch',
    'poor': 'p-U-r', 'young': 'y-V-ng', 'old': 'oU-l-d', 'cold': 'k-oU-l-d',
    'warm': 'w-O-r-m', 'sweet': 's-w-i-t', 'sick': 's-I-k', 'sad': 's-A-d',
    'please': 'p-l-i-z', 'sorry': 's-O-r-i', 'thank': 'th-A-ng-k',
    'baby': 'b-eI-b-i', 'darling': 'd-a-r-l-I-ng', 'mister': 'm-I-s-t-R',
}
