
from enum import *

class ENet_Event( IntEnum ):
    ClientConnected    = auto()
    ClientDisconnected = auto()

    ObjCreated         = auto()
    ObjPrepareDelete   = auto()
    ObjDeleted         = auto()

    ObjPropCreated     = auto()
    ObjPropDeleted     = auto()
    ObjPropUpdated     = auto()
