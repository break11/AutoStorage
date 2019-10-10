from enum import Enum, auto

class EAgentServer_Event( Enum ):
    # FakeAgentDevPacket = auto() # специальные команды для взаимодействия с фейк агентом - например команда об окончании заряда
    Error              = auto() # Error text message with symbol*
    Warning_           = auto() # Warning text message with symbol #
    Text               = auto() # Text message to Log
    HelloWorld         = auto() # @HW
    Accepted           = auto() # AC
    BatteryState       = auto() # @BS
    TemperatureState   = auto() # @TS
    TaskList           = auto() # @TL
    WheelOrientation   = auto() # @WO
    NewTask            = auto() # @NT
    PowerEnable        = auto() # @PE
    PowerDisable       = auto() # @PD
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
    ChargeMe           = auto() # @CM
    ChargeBegin        = auto() # @CB
    ChargeEnd          = auto() # @CE
    ServiceLog         = auto() # @SL
    OK                 = auto() # @OK

    @classmethod
    def fromBStr( cls, data ):
        return _AgentServer_Event_from_BStr.get( data )

    @classmethod
    def fromStr( cls, data ):
        return cls.fromBStr( data.encode() )
        
    def toStr( self ):
        return _AgentServer_Event_to_Str.get( self )

OD_OP_events = [EAgentServer_Event.OdometerDistance, EAgentServer_Event.OdometerPassed]

_AgentServer_Event_from_BStr = {
                                # b"@FA": EAgentServer_Event.FakeAgentDevPacket,
                                b"*"  : EAgentServer_Event.Error,
                                b"#"  : EAgentServer_Event.Warning_,
                                b""   : EAgentServer_Event.Text,
                                b"@HW": EAgentServer_Event.HelloWorld,
                                b"@AC": EAgentServer_Event.Accepted,
                                b"@BS": EAgentServer_Event.BatteryState,
                                b"@TS": EAgentServer_Event.TemperatureState,
                                b"@TL": EAgentServer_Event.TaskList,
                                b"@WO": EAgentServer_Event.WheelOrientation,
                                b"@NT": EAgentServer_Event.NewTask,
                                b"@PE": EAgentServer_Event.PowerEnable,
                                b"@PD": EAgentServer_Event.PowerDisable,
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
                                b"@BU": EAgentServer_Event.BoxUnload,
                                b"@BA": EAgentServer_Event.BoxLoadAborted,
                                b"@CM": EAgentServer_Event.ChargeMe,
                                b"@CB": EAgentServer_Event.ChargeBegin,
                                b"@CE": EAgentServer_Event.ChargeEnd,
                                b"@SL": EAgentServer_Event.ServiceLog,
                                b"@OK": EAgentServer_Event.OK,
                               }

_AgentServer_Event_to_Str = {}
for k, v in _AgentServer_Event_from_BStr.items():
    _AgentServer_Event_to_Str[ v ] = k.decode()
