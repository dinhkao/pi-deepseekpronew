#!/usr/bin/env python3
"""Render The Collector — bai 1 cua Revolver Sessions.

Chay tu repo root:  python3 songs/song01_the_collector/main.py
Ra file vao output/song01_the_collector/
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from songs.song01_the_collector.song import Collector
from songs._engine import Song

if __name__ == '__main__':
    outdir = os.path.join('output', Collector.name)
    s = Collector()
    mp3 = s.render(outdir)
    zp = s.zip_sources(outdir)
    print('OK:', mp3)
    print('OK:', zp)
