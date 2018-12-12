
from .Net_Events import ENet_Event as EV

from .NetObj_Manager import CNetObj_Manager

class CNetCmd:
    def __init__(self, Client_ID=None, Event=None, Obj_UID=None, PropName=None, ExtCmdData=None ):
        self.Client_ID = Client_ID
        if self.Client_ID is None: self.Client_ID = CNetObj_Manager.clientID
        assert Event in EV, f"Unsupported Event type {Event}"
        self.Event = Event
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
        ev         = EV( int( l[1] ) )

        if ev <= EV.ClientDisconnected:
            return CNetCmd( Client_ID=Client_UID, Event=ev )

        objUID    = int( l[2] )
        if ev <= EV.ObjDeleted:
            return CNetCmd( Client_ID=Client_UID, Event=ev, Obj_UID=objUID )

        if ev <= EV.ObjPropUpdated:
            propName = l[3]
            return CNetCmd( Client_ID=Client_UID, Event=ev, Obj_UID=objUID, PropName=propName )

        if ev > EV.ObjPropUpdated:
            extCmdData = l[3]
            return CNetCmd( Client_ID=Client_UID, Event=ev, Obj_UID=objUID, ExtCmdData=extCmdData )

    def __repr__(self): return self.toString( bDebug = True )
