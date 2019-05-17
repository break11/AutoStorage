from enum import IntEnum, auto

class EAgentServer_Event( IntEnum ):
    HelloWorld       = auto() # @HW
    ClientAccepting  = auto() # @CA
    ServerAccepting  = auto() # @SA
    BatteryState     = auto() # @BS
    TemperatureState = auto() # @TS

    @classmethod
    def fromBStr( cls, data ):
        return _AgentServer_Event_from_BStr.get( data )

    def toStr( self ):
        return _AgentServer_Event_to_Str[ self ]

_AgentServer_Event_from_BStr = {
                                b"@HW": EAgentServer_Event.HelloWorld,
                                b"@CA": EAgentServer_Event.ClientAccepting,
                                b"@SA": EAgentServer_Event.ServerAccepting,
                                b"@BS": EAgentServer_Event.BatteryState,
                                b"@TS": EAgentServer_Event.TemperatureState,
                               }

_AgentServer_Event_to_Str = {}
for k, v in _AgentServer_Event_from_BStr.items():
    _AgentServer_Event_to_Str[ v ] = k.decode()
