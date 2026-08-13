"""bass — bass"""

from .natbass import natbass
from .fretless import fretless
from .upright import upright
from .moogbass import moogbass
from .jugbass import jugbass
from .BassPlayer import BassPlayer
from .pluck import pluck
from .walk import walk
from .amp import amp

__all__ = ['BassPlayer', 'amp', 'fretless', 'jugbass', 'moogbass', 'natbass', 'pluck', 'upright', 'walk']
