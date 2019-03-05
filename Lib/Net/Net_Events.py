
from enum import IntEnum, auto

class ENet_Event( IntEnum ):
    ClientConnected    = auto()
    ClientDisconnected = auto()

    ObjCreated         = auto()
    ObjPrepareDelete   = auto()
    ObjDeleted         = auto() # по сети не отправляется - только для callback-ов

    ObjPropCreated     = auto()
    ObjPropDeleted     = auto()
    ObjPropUpdated     = auto()
