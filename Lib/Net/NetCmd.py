
from .Net_Events import ENet_Event as EV
from  Lib.Common.StrTypeConverter import CStrTypeConverter

class CNetCmd:
    def __init__(self, Event=None, Obj_UID=None, PropName=None, ExtCmdData=None, value=None ):
        assert Event in EV, f"Unsupported Event type {Event}"
        self.Event = Event
        self.Obj_UID = Obj_UID
        self.sPropName = PropName
        self.value = value
        self.ExtCmdData = ExtCmdData

    def toString( self, bDebug = False ):
        cmd = self.Event.name if bDebug else self.Event
        if   self.Event <= EV.ClientDisconnected: return f"{cmd}"
        elif self.Event <= EV.ObjDeleted:         return f"{cmd}:{self.Obj_UID}"
        elif self.Event <= EV.ObjPropUpdated:     return f"{cmd}:{self.Obj_UID}:{self.sPropName}:{self.value}"
        elif self.Event >  EV.ObjPropUpdated:     return f"{cmd}:{self.Obj_UID}:{self.ExtCmdData}"

    @staticmethod
    def fromString( sVal ):
        l = sVal.split(":")

        ev = EV( int( l[0] ) )

        if ev <= EV.ClientDisconnected:
            return CNetCmd( Event=ev )
        else:
            Obj_UID    = int( l[1] )
            if ev <= EV.ObjDeleted:
                return CNetCmd( Event=ev, Obj_UID=Obj_UID )
            elif ev <= EV.ObjPropUpdated:
                propName  = l[2]
                value     = l[3]
                return CNetCmd( Event=ev, Obj_UID=Obj_UID, PropName=propName, value=value )

            elif ev > EV.ObjPropUpdated:
                extCmdData = l[2]
                return CNetCmd( Event=ev, Obj_UID=Obj_UID, ExtCmdData=extCmdData )

    def __repr__(self): return self.toString( bDebug = True )
