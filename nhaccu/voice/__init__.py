"""voice — giong hat"""

from .sing import sing
from .phon import phon
from .g2p import g2p
from .vline import vline
from .vdouble import vdouble
from .vharm import vharm
from .gang import gang
from .spoken import spoken
from .oohs import oohs
from .choir_satb import choir_satb
from .gospel import gospel
from .falsetto_stack import falsetto_stack
from .preacher import preacher
from .crowd import crowd
from .lead import lead
from .lead_soft import lead_soft
from .lead_double import lead_double

__all__ = ['choir_satb', 'crowd', 'falsetto_stack', 'g2p', 'gang', 'gospel', 'lead', 'lead_double', 'lead_soft', 'oohs', 'phon', 'preacher', 'sing', 'spoken', 'vdouble', 'vharm', 'vline']
