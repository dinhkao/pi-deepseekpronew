"""Nghe thu mot file bang Gemini va nhan xet (dung API key).

    python3 songs/_listen.py <file.mp3> [cau hoi them]
"""
from __future__ import annotations

import base64
import json
import os
import sys
import urllib.request

KEY = os.environ.get('GEMINI_API_KEY',
                     'AIzaSyAT0q7fmQ-BpQDEQfFbeTQ3DruziYQPRYo')
MODEL = 'gemini-flash-latest'
URL = ('https://generativelanguage.googleapis.com/v1beta/models/%s'
       ':generateContent?key=%s' % (MODEL, KEY))


def listen(path, question=None):
    with open(path, 'rb') as f:
        data = base64.b64encode(f.read()).decode()
    q = question or (
        'Day la mot bai hat duoc tong hop bang python lay cam hung tu album '
        'Revolver cua The Beatles. Hay nghe ky va nhan xet bang tieng Viet: '
        '1) phan hoa am co cho nao nghe lech tone/sai not khong, o phut nao; '
        '2) tieng trong co dung nhịp/khong roi rac khong; '
        '3) mix co thieu/thua tan so nao khong (qua chua, qua duc, thieu bass); '
        '4) giong hat co nghe ro loi khong; '
        '5) cau truc bai (verse/refrain/bridge) co ro rang khong; '
        '6) 3 dieu nen sua de hay hon. Tra loi ngan gon, cu the.')
    body = {
        'contents': [{
            'parts': [
                {'inline_data': {'mime_type': 'audio/mpeg', 'data': data}},
                {'text': q},
            ]
        }]
    }
    req = urllib.request.Request(
        URL, data=json.dumps(body).encode(),
        headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=300) as r:
        out = json.loads(r.read())
    try:
        return out['candidates'][0]['content']['parts'][0]['text']
    except Exception:
        return json.dumps(out)[:2000]


if __name__ == '__main__':
    print(listen(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None))
