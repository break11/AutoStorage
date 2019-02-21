
from enum import IntEnum, auto

class ENet_Event( IntEnum ):
    ClientConnected    = auto()
    ClientDisconnected = auto()

    ObjCreated         = auto()
    ObjPrepareDelete   = auto()
    # ObjDeleted         = auto() # причина вывода команды описана в CNetObj_Manager.unregisterObj - забивание канала лишними командами

    ObjPropCreated     = auto()
    ObjPropDeleted     = auto()
    ObjPropUpdated     = auto()
