
from .Net_Events import ENet_Event as EV

class CNetCmd:
    def __init__(self, Client_ID, CMD, Obj_UID=None, PropName=None, ExtCmdData=None ):
        self.Client_ID = Client_ID
        self.Event = CMD
        self.Obj_UID = Obj_UID
        self.sPropName = PropName
        self.ExtCmdData = ExtCmdData

    def toString( self, bDebug = False ):
        cmd = self.Event.name if bDebug else self.Event
        if self.Event <= EV.ClientDisconnected: return f"{self.Client_ID}:{cmd}"
        if self.Event <= EV.ObjDeleted:         return f"{self.Client_ID}:{cmd}:{self.Obj_UID}"
        if self.Event <= EV.ObjPropUpdated:     return f"{self.Client_ID}:{cmd}:{self.Obj_UID}:{self.sPropName}"
        if self.Event >  EV.ObjPropUpdated:     return f"{self.Client_ID}:{cmd}:{self.Obj_UID}:{self.ExtCmdData}"

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