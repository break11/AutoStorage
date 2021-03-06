from enum import Enum, auto

class EAgentServer_Event( Enum ):
    Error              = auto() # ER
    Warning_           = auto() # WR
    Text               = auto() # TX
    HelloWorld         = auto() # HW
    Accepted           = auto() # AC
    BatteryState       = auto() # BS
    TemperatureState   = auto() # TS
    TaskList           = auto() # TL
    WheelOrientation   = auto() # WO
    NewTask            = auto() # NT
    PowerEnable        = auto() # PE
    PowerDisable       = auto() # PD
    BrakeRelease       = auto() # BR
    EmergencyStop      = auto() # ES
    SequenceBegin      = auto() # SB
    SequenceEnd        = auto() # SE
    DistancePassed     = auto() # DP
    OdometerZero       = auto() # OZ
    OdometerDistance   = auto() # OD
    DistanceEnd        = auto() # DE
    BoxLoad            = auto() # BL
    BoxUnload          = auto() # BU
    BoxLoadAborted     = auto() # BA
    ChargeMe           = auto() # CM
    ChargeBegin        = auto() # CB
    ChargeEnd          = auto() # CE
    ServiceLog         = auto() # SL
    OK                 = auto() # OK
    Idle               = auto() # ID

    def __str__( self ): return self.toStr()

    @classmethod
    def fromStr( cls, data ):
        return _AgentServer_Event_from_Str.get( data )
        
    def toStr( self ):
        return _AgentServer_Event_to_Str.get( self )

_AgentServer_Event_from_Str = {
                                "ER": EAgentServer_Event.Error,
                                "WR": EAgentServer_Event.Warning_,
                                "TX": EAgentServer_Event.Text,
                                "HW": EAgentServer_Event.HelloWorld,
                                "AC": EAgentServer_Event.Accepted,
                                "BS": EAgentServer_Event.BatteryState,
                                "TS": EAgentServer_Event.TemperatureState,
                                "TL": EAgentServer_Event.TaskList,
                                "WO": EAgentServer_Event.WheelOrientation,
                                "NT": EAgentServer_Event.NewTask,
                                "PE": EAgentServer_Event.PowerEnable,
                                "PD": EAgentServer_Event.PowerDisable,
                                "BR": EAgentServer_Event.BrakeRelease,
                                "ES": EAgentServer_Event.EmergencyStop,
                                "SB": EAgentServer_Event.SequenceBegin,
                                "SE": EAgentServer_Event.SequenceEnd,
                                "DP": EAgentServer_Event.DistancePassed,
                                "OZ": EAgentServer_Event.OdometerZero,
                                "OD": EAgentServer_Event.OdometerDistance,
                                "DE": EAgentServer_Event.DistanceEnd,
                                "BL": EAgentServer_Event.BoxLoad,
                                "BU": EAgentServer_Event.BoxUnload,
                                "BA": EAgentServer_Event.BoxLoadAborted,
                                "CM": EAgentServer_Event.ChargeMe,
                                "CB": EAgentServer_Event.ChargeBegin,
                                "CE": EAgentServer_Event.ChargeEnd,
                                "SL": EAgentServer_Event.ServiceLog,
                                "OK": EAgentServer_Event.OK,
                                "ID": EAgentServer_Event.Idle,
                              }

_AgentServer_Event_to_Str = {}
for k, v in _AgentServer_Event_from_Str.items():
    _AgentServer_Event_to_Str[ v ] = k
