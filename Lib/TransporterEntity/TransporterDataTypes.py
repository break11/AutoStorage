
from enum import auto

from Lib.Common.BaseEnum import BaseEnum

class ETransporterMode( BaseEnum ):
    SingleBox = auto()
    MultiBox  = auto()

    Undefined = auto()
    Default   = SingleBox
