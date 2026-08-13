#!/usr/bin/env python3
"""Render Under the Orange Sea — bai 6 cua Revolver Sessions (YS DNA)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from songs.song06_under_the_orange_sea.song import UnderTheOrangeSea

if __name__ == '__main__':
    outdir = os.path.join('output', UnderTheOrangeSea.name)
    s = UnderTheOrangeSea()
    mp3 = s.render(outdir)
    zp = s.zip_sources(outdir)
    print('OK:', mp3)
    print('OK:', zp)
