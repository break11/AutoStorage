from enum import Enum, auto

class EAgentServer_Event( Enum ):
    FakeAgentDevPacket = auto() # специальные команды для взаимодействия с фейк агентом - например команда об окончании заряда
    Error              = auto() # Error text message with symbol*
    Warning_           = auto() # Warning text message with symbol #
    Text               = auto() # Text message to Log
    HelloWorld         = auto() # @HW
    ClientAccepting    = auto() # @CA
    ServerAccepting    = auto() # @SA
    BatteryState       = auto() # @BS
    TemperatureState   = auto() # @TS
    TaskList           = auto() # @TL
    WheelOrientation   = auto() # @WO
    NewTask            = auto() # @NT
    PowerOn            = auto() # @PE
    PowerOff           = auto() # @PD
    BrakeRelease       = auto() # @BR
    EmergencyStop      = auto() # @ES
    SequenceBegin      = auto() # @SB
    SequenceEnd        = auto() # @SE
    DistancePassed     = auto() # @DP
    OdometerZero       = auto() # @OZ
    OdometerPassed     = auto() # @OP
    OdometerDistance   = auto() # @OD
    DistanceEnd        = auto() # @DE
    BoxLoad            = auto() # @BL
    BoxUnload          = auto() # @BU
    BoxLoadAborted     = auto() # @BA

    @classmethod
    def fromBStr( cls, data ):
        return _AgentServer_Event_from_BStr.get( data )

    @classmethod
    def fromStr( cls, data ):
        return cls.fromBStr( data.encode() )
        
    def toStr( self ):
        return _AgentServer_Event_to_Str.get( self )

_AgentServer_Event_from_BStr = {
                                b"@FA": EAgentServer_Event.FakeAgentDevPacket,
                                b"*"  : EAgentServer_Event.Error,
                                b"#"  : EAgentServer_Event.Warning_,
                                b""   : EAgentServer_Event.Text,
                                b"@HW": EAgentServer_Event.HelloWorld,
                                b"@CA": EAgentServer_Event.ClientAccepting,
                                b"@SA": EAgentServer_Event.ServerAccepting,
                                b"@BS": EAgentServer_Event.BatteryState,
                                b"@TS": EAgentServer_Event.TemperatureState,
                                b"@TL": EAgentServer_Event.TaskList,
                                b"@WO": EAgentServer_Event.WheelOrientation,
                                b"@NT": EAgentServer_Event.NewTask,
                                b"@PE": EAgentServer_Event.PowerOn,
                                b"@PD": EAgentServer_Event.PowerOff,
                                b"@BR": EAgentServer_Event.BrakeRelease,
                                b"@ES": EAgentServer_Event.EmergencyStop,
                                b"@SB": EAgentServer_Event.SequenceBegin,
                                b"@SE": EAgentServer_Event.SequenceEnd,
                                b"@DP": EAgentServer_Event.DistancePassed,
                                b"@OZ": EAgentServer_Event.OdometerZero,
                                b"@OP": EAgentServer_Event.OdometerPassed,
                                b"@OD": EAgentServer_Event.OdometerDistance,
                                b"@DE": EAgentServer_Event.DistanceEnd,
                                b"@BL": EAgentServer_Event.BoxLoad,
                                b"@DU": EAgentServer_Event.BoxUnload,
                                b"@BA": EAgentServer_Event.BoxLoadAborted
                               }

_AgentServer_Event_to_Str = {}
for k, v in _AgentServer_Event_from_BStr.items():
    _AgentServer_Event_to_Str[ v ] = k.decode()
