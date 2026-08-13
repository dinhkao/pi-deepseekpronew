#!/usr/bin/env python3
"""Render The Long Goodbye — bai 10 cua Revolver Sessions (TNK+GTGYIML DNA)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from songs.song10_the_long_goodbye.song import TheLongGoodbye

if __name__ == '__main__':
    outdir = os.path.join('output', TheLongGoodbye.name)
    s = TheLongGoodbye()
    mp3 = s.render(outdir)
    zp = s.zip_sources(outdir)
    print('OK:', mp3)
    print('OK:', zp)
