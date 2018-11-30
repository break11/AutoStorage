
from .Net_Events import ENet_Event as EV

class CNetCmd:
    def __init__(self, Client_UID, CMD, Obj_UID=None, Prop_Name=None, ExtCmdData=None ):
        self.Client_UID = Client_UID
        self.CMD = CMD
        self.Obj_UID = Obj_UID
        self.sProp_Name = Prop_Name
        self.ExtCmdData = ExtCmdData

    def toString( self, bDebug = False ):
        cmd = self.CMD.name if bDebug else self.CMD
        if self.CMD <= EV.ClientDisconnected: return f"{self.Client_UID}:{cmd}"
        if self.CMD <= EV.ObjDeleted:         return f"{self.Client_UID}:{cmd}:{self.Obj_UID}"
        if self.CMD <= EV.ObjPropUpdated:    return f"{self.Client_UID}:{cmd}:{self.Obj_UID}:{self.sProp_Name}"
        if self.CMD >  EV.ObjPropUpdated:     return f"{self.Client_UID}:{cmd}:{self.Obj_UID}:{self.ExtCmdData}"

    @staticmethod
    def fromString( sVal ):
        l = sVal.split(":")

        Client_UID = int( l[0] )
        cmd        = EV( int( l[1] ) )

        if cmd <= EV.ClientDisconnected:
            return CNetCmd( Client_UID, cmd )

        Obj_UID    = int( l[2] )
        if cmd <= EV.ObjDeleted:
            return CNetCmd( Client_UID, cmd, Obj_UID )

        if cmd <= EV.ObjPropUpdated:
            PropName = l[3]
            return CNetCmd( Client_UID, cmd, Obj_UID, PropName )

        if cmd > EV.ObjPropUpdated:
            ExtCmdData = l[3]
            return CNetCmd( Client_UID, cmd, Obj_UID, ExtCmdData )

    def __repr__(self): return self.toString( bDebug = True )