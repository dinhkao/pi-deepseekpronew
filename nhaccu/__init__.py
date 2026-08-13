"""nhaccu — moi nhac cu cua geese-3d-country mot file .py.

    from nhaccu.guitar.fuzz import fuzz
    from nhaccu import fuzz            # cung duoc

Xem README.md de biet cach dung.
"""

from ._dsp import *   # noqa: F401,F403
from ._core import *  # noqa: F401,F403
from .bass import *  # noqa: F401,F403
from .guitar import *  # noqa: F401,F403
from .keys import *  # noqa: F401,F403
from .mallet import *  # noqa: F401,F403
from .string_section import *  # noqa: F401,F403
from .folk import *  # noqa: F401,F403
from .horns import *  # noqa: F401,F403
from .voice import *  # noqa: F401,F403
from .drums import *  # noqa: F401,F403
from .percussion import *  # noqa: F401,F403
from .fx import *  # noqa: F401,F403
from ._lib.inst import LVL, GAIN, lvl, ks, damp  # noqa: F401
from ._lib.horns import VOICES, QUARTET, BRASS4, REEDS, SALVATION  # noqa: F401
