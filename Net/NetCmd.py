
from .Net_Events import ENet_Event as EV
from Common.StrTypeConverter import CStrTypeConverter

class CNetCmd:
    def __init__(self, Event=None, Obj_UID=None, PropName=None, ExtCmdData=None ):
        assert Event in EV, f"Unsupported Event type {Event}"
        self.Event = Event
        self.Obj_UID = Obj_UID
        self.sPropName = PropName
        self.ExtCmdData = ExtCmdData

    def toString( self, bDebug = False ):
        cmd = self.Event.name if bDebug else self.Event
        if   self.Event <= EV.ClientDisconnected: return f"{cmd}"
        elif self.Event <= EV.ObjPrepareDelete:   return f"{cmd}:{self.Obj_UID}"
        elif self.Event <= EV.ObjPropUpdated:     return f"{cmd}:{self.Obj_UID}:{self.sPropName}"
        elif self.Event >  EV.ObjPropUpdated:     return f"{cmd}:{self.Obj_UID}:{self.ExtCmdData}"

    @staticmethod
    def fromString( sVal ):
        l = sVal.split(":")

        ev         = EV( int( l[0] ) )

        if ev <= EV.ClientDisconnected:
            return CNetCmd( Event=ev )
        else:
            objUID    = int( l[1] )
            if ev <= EV.ObjPrepareDelete:
                return CNetCmd( Event=ev, Obj_UID=objUID )
            elif ev <= EV.ObjPropUpdated:
                propName  = l[2]
                return CNetCmd( Event=ev, Obj_UID=objUID, PropName=propName )

            elif ev > EV.ObjPropUpdated:
                extCmdData = l[2]
                return CNetCmd( Event=ev, Obj_UID=objUID, ExtCmdData=extCmdData )

    def __repr__(self): return self.toString( bDebug = True )

from .NetObj_Manager import CNetObj_Manager
