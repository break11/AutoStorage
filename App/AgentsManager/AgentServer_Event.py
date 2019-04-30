from enum import IntEnum, auto

class EAgentServer_Event( IntEnum ):
    HelloWorld      = auto() # @HW
    ClientAccepting = auto() # @CA
    ServerAccepting = auto() # @SA
    BatteryState    = auto() # @BS

    @classmethod
    def fromBStr( cls, data ):
        return _AgentServer_Event_from_BStr.get( data )

    @classmethod
    def toStr( cls, data ):
        return _AgentServer_Event_to_Str[ data ]

_AgentServer_Event_from_BStr = {
                                b"@HW": EAgentServer_Event.HelloWorld,
                                b"@CA": EAgentServer_Event.ClientAccepting,
                                b"@SA": EAgentServer_Event.ServerAccepting,
                                b"@BS": EAgentServer_Event.BatteryState,
                               }

_AgentServer_Event_to_Str = {}
for k, v in _AgentServer_Event_from_BStr.items():
    _AgentServer_Event_to_Str[ v ] = k.decode()
