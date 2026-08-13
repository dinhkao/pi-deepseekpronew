#!/usr/bin/env python3
"""Render She Never Said — bai 7 cua Revolver Sessions (SSSS DNA)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from songs.song07_she_never_said.song import SheNeverSaid

if __name__ == '__main__':
    outdir = os.path.join('output', SheNeverSaid.name)
    s = SheNeverSaid()
    mp3 = s.render(outdir)
    zp = s.zip_sources(outdir)
    print('OK:', mp3)
    print('OK:', zp)
