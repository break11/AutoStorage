
from enum import *

class ECmd( IntEnum ):
    client_connected    = auto()
    client_disconnected = auto()
    obj_created         = auto()
    obj_deleted         = auto()
    # obj_updated         = auto()
    obj_prop_created    = auto()
    obj_prop_deleted    = auto()
    obj_prop_updated    = auto()

class CNetCmd:
    def __init__(self, Client_UID, CMD, Obj_UID ):
        self.Client_UID = Client_UID
        self.CMD = CMD
        self.Obj_UID = Obj_UID

    def toString( self ):
        return f"{self.Client_UID}:{self.CMD}:{self.Obj_UID}"

    @staticmethod
    def fromString( sVal ):
        l = sVal.split(":")

        Client_UID = int( l[0] )
        cmd        = ECmd( int( l[1] ) )
        Obj_UID    = int( l[2] )

        return CNetCmd( Client_UID, cmd, Obj_UID )

    def __repr__(self): return f"<{self.Client_UID}:{self.CMD.name}:{self.Obj_UID}>"
