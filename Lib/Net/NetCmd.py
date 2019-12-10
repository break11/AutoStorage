
from enum import IntEnum, auto

from .Net_Events import ENet_Event as EV
from  Lib.Common.StrTypeConverter import CStrTypeConverter

ObjProp_Event_Group = [ EV.ObjPropCreated, EV.ObjPropDeleted, EV.ObjPropUpdated ]
Obj_Event_Group     = ObjProp_Event_Group + [ EV.ObjCreated, EV.ObjPrepareDelete, EV.ObjDeleted ]

class ENetCmd_ElemntPosition( IntEnum ):
    EventType = 0
    Obj_UID   = auto()
    PropName  = auto()
    PropValue = auto()
    PropType  = auto()

EPos = ENetCmd_ElemntPosition

class CNetCmd:
    DS = ":"
    def __init__(self, Event=None, Obj_UID=None, PropName=None, value=None ):
        assert Event in EV, f"Unsupported Event type {Event}"
        self.Event = Event
        self.Obj_UID = Obj_UID
        self.sPropName = PropName
        self.value = value

    def toString( self, bDebug = False ):
        cmd = self.Event.name if bDebug else self.Event

        Obj_UID, sPropName, sPropValue, sPropType = "", "", "", ""

        if self.Event in Obj_Event_Group:
            Obj_UID   = self.Obj_UID

        if self.Event in ObjProp_Event_Group:
            sPropName  = self.sPropName
            sPropValue = CStrTypeConverter.ValToStr(self.value)
            if self.Event == EV.ObjPropCreated:
                sPropType = type( self.value ).__name__

        return f"{cmd}{ self.DS }{Obj_UID}{ self.DS }{sPropName}{ self.DS }{sPropValue}{ self.DS }{sPropType}"
        
    @staticmethod
    def fromString( sVal ):
        l = sVal.split(":")

        ev = EV( int( l[ EPos.EventType ] ) )

        Obj_UID, propName, value, propType = None, None, None, None

        if ev in Obj_Event_Group:
            Obj_UID = int( l[ EPos.Obj_UID ] )
        
        if ev in ObjProp_Event_Group:
            propName  = l[ EPos.PropName ]
            obj    = CNetObj_Manager.accessObj( Obj_UID, genAssert=True )
            if ev == EV.ObjPropCreated:
                propType = eval( l[ EPos.PropType ] )
            else:
                propType = type( obj[ propName ] )
            value  = CStrTypeConverter.ValFromStr( propType, l[ EPos.PropValue ] )

        return CNetCmd( Event=ev, Obj_UID=Obj_UID, PropName=propName, value=value )

    def __str__(self): return self.toString( bDebug = True )

    def __eq__(self, other):
        eq = True
        eq = eq and self.Event      == other.Event
        eq = eq and self.Obj_UID    == other.Obj_UID
        eq = eq and self.sPropName  == other.sPropName
        eq = eq and self.value      == other.value

        return eq

from .NetObj_Manager import CNetObj_Manager
