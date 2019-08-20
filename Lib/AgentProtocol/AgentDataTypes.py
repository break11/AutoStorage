
from enum import auto
from Lib.Common.BaseEnum import BaseEnum
from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event as AEV
from Lib.Common import StorageGraphTypes as SGT

TeleEvents = { AEV.BatteryState, AEV.TemperatureState, AEV.TaskList, AEV.OdometerPassed }
BL_BU_Events = { AEV.BoxLoad, AEV.BoxUnload }

class EAgent_CMD_State( BaseEnum ):
    Init = auto()
    Done = auto()
    Default = Done

class EAgent_Status( BaseEnum ):
    Idle            = auto()
    GoToCharge      = auto()
    Charging        = auto()
    OnRoute         = auto() 
    NoRouteToCharge = auto() # не найден маршрут к зарядке - зарядки нет на графе или неправильный угол челнока 
    PosSyncError    = auto() # ошибка синхронизации по графу - несоответствие реального положения челнока и положения в программе
    CantCharge      = auto() # нет свойства с именем chargePort в ноде зарядки
    AgentError      = auto() # пришла ошибка с тележки

    BoxLoad_Right   = auto()
    BoxLoad_Left    = auto()
    BoxUnload_Right = auto()
    BoxUnload_Left  = auto()

    Default         = Idle

blockAutoControlStatuses = [ EAgent_Status.NoRouteToCharge, EAgent_Status.PosSyncError, EAgent_Status.CantCharge, EAgent_Status.AgentError ]

BL_BU_Agent_Status = { (AEV.BoxLoad, SGT.ESide.Left)    : EAgent_Status.BoxLoad_Left,
                       (AEV.BoxLoad, SGT.ESide.Right)   : EAgent_Status.BoxLoad_Right,
                       (AEV.BoxUnload, SGT.ESide.Left)  : EAgent_Status.BoxUnload_Left,
                       (AEV.BoxUnload, SGT.ESide.Right) : EAgent_Status.BoxUnload_Right,
                    }

BL_BU_Agent_Status_vals = BL_BU_Agent_Status.values()

#########################################################

class EAgentBattery_Type( BaseEnum ):
    Supercap   = auto()
    Li         = auto()
    N          = auto()
    S = Supercap
    L = Li

    Default    = Supercap

    def toString( self ):
        toStrD = { EAgentBattery_Type.Supercap: "S",
                   EAgentBattery_Type.Li      : "L",
                   EAgentBattery_Type.N       : "N"
                 }
        return toStrD[ self ]


class SAgent_BatteryState:
    C = 1000
    max_S_U = 43.2
    min_S_U = 25
    E_full  = 0.5 * C * (max_S_U ** 2)
    E_empty = 0.5 * C * (min_S_U ** 2)

    def __init__( self, PowerType, S_V, L_V, power_U, power_I1, power_I2 ):
        self.PowerType = PowerType
        self.S_V = S_V
        self.L_V = L_V
        self.power_U = power_U
        self.power_I1 = power_I1
        self.power_I2 = power_I2

    def supercapPercentCharge( self ):
        E = 0.5 * self.C * (self.S_V ** 2)
        return 100 * ( max(E - self.E_empty, 0) ) / ( self.E_full - self.E_empty )

    @classmethod
    def fromString( cls, data ):
        "S,33.44V,40.00V,47.64V,01.1A/00.3A"
        l = data.split( "," )
        
        PowerType = EAgentBattery_Type.fromString( l[0] )
        S_V       = float( l[1][:-1] )
        L_V       = float( l[2][:-1] )
        power_U   = float( l[3][:-1] )

        I = l[4].split( "/" )
        power_I1 = float( I[0][:-1] )
        power_I2 = float( I[1][:-1] )

        return SAgent_BatteryState( PowerType, S_V, L_V, power_U, power_I1, power_I2 )
    
    def toString( self ):
        return f"{ EAgentBattery_Type.toString( self.PowerType ) },{self.S_V:05.2f}V,{self.L_V:05.2f}V,{self.power_U:05.2f}V,{self.power_I1:04.1f}A/{self.power_I2:04.1f}A"

#########################################################

class SFakeAgent_DevPacketData:
    "Charging,XXX,XXX"
    "1,XXX,XXX"

    def __init__( self, bCharging ):
        self.bCharging = bCharging
    
    @classmethod
    def fromString( cls, data ):
        params = data.split(",")
        return SFakeAgent_DevPacketData( bCharging = bool( int( params[ 0 ] ) ) )

    def toString( self ):
        cmds = []
        cmds.append( str( int( self.bCharging ) ) )

        return ",".join( cmds )

#########################################################
class SHW_Data:
    "000"
    "056"
    def __init__( self, lastRXPacketN ):
        self.lastRXPacketN = lastRXPacketN
        self.bIsValid = True

    @classmethod
    def fromString( cls, data ):
        try:
            lastRXPacketN = int( data )
            bIsValid = True
        except:
            lastRXPacketN = 0
            bIsValid = False

        HW_Data = SHW_Data( lastRXPacketN )
        HW_Data.bIsValid = bIsValid

        return HW_Data

    def toString( self ):
        return f"{self.lastRXPacketN:03d}"

#########################################################

class SOD_OP_Data:
    "@OD:100"
    "@OP:138"
    "OP:U"

    def __init__( self, bUndefined=True, nDistance=0 ):
        self.bUndefined = bUndefined
        self.nDistance = nDistance

    def getDistance( self ): return 0 if self.bUndefined else self.nDistance

    @classmethod
    def fromString( cls, data ):
        try:
            bUndefined = False
            nDistance = int( data )
        except:
            bUndefined = True
            nDistance = 0

        return SOD_OP_Data( bUndefined = bUndefined, nDistance = nDistance )

    def toString( self ):
        if not self.bUndefined:
            sResult = str( self.nDistance )
        else:
            sResult = "U"

        return sResult

class SNT_Data:
    sIdle = "ID"

    def __init__(self, event, data, bIdle = False):
        self.bIdle = bIdle
        self.event = event
        self.data = data

    @classmethod
    def fromString( cls, data ):
        if data == cls.sIdle:
            return SNT_Data( event = None, data = None, bIdle = True )

        l = data.split(",")
        event = AEV.fromStr( "@" + l[0] )
        nt_data = None

        if event in BL_BU_Events:
            nt_data = SGT.ESide.fromChar( l[1] )
        
        return SNT_Data( event, nt_data )

    def toString( self ):
        if self.bIdle: return self.sIdle

        sResult = self.event.tostr()[1:]

        if self.event in BL_BU_Events:
            sResult += SGT.ESide.toChar()

        return sResult

    
