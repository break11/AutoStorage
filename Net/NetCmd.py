
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
    def __init__(self, Client_UID, CMD, Obj_UID=None, Prop_Name=None, ExtCmdData=None ):
        self.Client_UID = Client_UID
        self.CMD = CMD
        self.Obj_UID = Obj_UID
        self.sProp_Name = Prop_Name
        self.ExtCmdData = ExtCmdData

    def toString( self, bDebug = False ):
        cmd = self.CMD.name if bDebug else self.CMD
        if self.CMD <= ECmd.client_disconnected: return f"{self.Client_UID}:{cmd}"
        if self.CMD <= ECmd.obj_deleted:         return f"{self.Client_UID}:{cmd}:{self.Obj_UID}"
        if self.CMD <= ECmd.obj_prop_updated:    return f"{self.Client_UID}:{cmd}:{self.Obj_UID}:{self.sProp_Name}"
        if self.CMD > ECmd.obj_prop_updated:     return f"{self.Client_UID}:{cmd}:{self.Obj_UID}:{self.ExtCmdData}"

    @staticmethod
    def fromString( sVal ):
        l = sVal.split(":")

        Client_UID = int( l[0] )
        cmd        = ECmd( int( l[1] ) )

        if cmd <= ECmd.client_disconnected:
            return CNetCmd( Client_UID, cmd )

        Obj_UID    = int( l[2] )
        if cmd <= ECmd.obj_deleted:
            return CNetCmd( Client_UID, cmd, Obj_UID )

        if cmd <= ECmd.obj_prop_updated:
            PropName = l[3]
            return CNetCmd( Client_UID, cmd, Obj_UID, PropName )

        if cmd > ECmd.obj_prop_updated:
            ExtCmdData = l[3]
            return CNetCmd( Client_UID, cmd, Obj_UID, ExtCmdData )

    def __repr__(self): return self.toString( bDebug = True )