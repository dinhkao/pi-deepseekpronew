#!/usr/bin/env python3
"""Render Raga for the Restless — bai 4 cua Revolver Sessions (Love You To DNA)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from songs.song04_raga_for_the_restless.song import RagaForTheRestless

if __name__ == '__main__':
    outdir = os.path.join('output', RagaForTheRestless.name)
    s = RagaForTheRestless()
    mp3 = s.render(outdir)
    zp = s.zip_sources(outdir)
    print('OK:', mp3)
    print('OK:', zp)
