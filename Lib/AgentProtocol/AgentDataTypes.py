
from enum import auto
from Lib.Common.BaseEnum import BaseEnum
from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event as AEV
from Lib.Common import StorageGraphTypes as SGT
import Lib.Common.StrConsts as SC

MS = "~" # Main Splitter
DS = "^" # Data Splitter

minChargeValue = 30

TeleEvents = { AEV.BatteryState, AEV.TemperatureState, AEV.TaskList, AEV.OdometerPassed }
BL_BU_Events = { AEV.BoxLoad, AEV.BoxUnload }

class EConnectedStatus( BaseEnum ):
    connected    = auto()
    disconnected = auto()
    freeze       = auto()
    Default      = disconnected

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

class SAgent_TemperatureState:
    sDefVal = f"24{DS}29{DS}29{DS}29{DS}29{DS}25{DS}25{DS}25{DS}25"
    def __init__( self, t1, t2, t3, t4, t5, t6, t7, t8, t9 ):
        self.t1 = t1
        self.t2 = t2
        self.t3 = t3
        self.t4 = t4
        self.t5 = t5
        self.t6 = t6
        self.t7 = t7
        self.t8 = t8
        self.t9 = t9

    def __str__( self ): return self.toString()

    @classmethod
    def defVal( cls ):
        return SAgent_TemperatureState.fromString( cls.sDefVal )

    @classmethod
    def fromString( cls, data ):
        try:
            l = data.split( DS )

            t1 = float( l[0] )
            t2 = float( l[1] )
            t3 = float( l[2] )
            t4 = float( l[3] )
            t5 = float( l[4] )
            t6 = float( l[5] )
            t7 = float( l[6] )
            t8 = float( l[7] )
            t9 = float( l[8] )

            return SAgent_TemperatureState( t1, t2, t3, t4, t5, t6, t7, t8, t9 )
        except:
            print( f"{SC.sWarning} {cls.__name__} can't construct from string '{data}', using default value '{cls.defVal()}'!" )
            return cls.defVal()

    def toString( self ):
        return f"{self.t1:.0f}{ DS }"\
               f"{self.t2:.0f}{ DS }"\
               f"{self.t3:.0f}{ DS }"\
               f"{self.t4:.0f}{ DS }"\
               f"{self.t5:.0f}{ DS }"\
               f"{self.t6:.0f}{ DS }"\
               f"{self.t7:.0f}{ DS }"\
               f"{self.t8:.0f}{ DS }"\
               f"{self.t9:.0f}"

class SAgent_BatteryState:
    sDefVal = f"S{DS}33.44V{DS}40.00V{DS}47.64V{DS}1.10A{DS}0.30A"
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

    def __str__( self ): return self.toString()

    def supercapPercentCharge( self ):
        E = 0.5 * self.C * (self.S_V ** 2)
        return 100 * ( max(E - self.E_empty, 0) ) / ( self.E_full - self.E_empty )

    @classmethod
    def defVal( cls ):
        return SAgent_BatteryState.fromString( cls.sDefVal )

    @classmethod
    def fromString( cls, data ):
        try:
            l = data.split( DS )
            
            PowerType = EAgentBattery_Type.fromString( l[0] )
            S_V       = float( l[1][:-1] )
            L_V       = float( l[2][:-1] )
            power_U   = float( l[3][:-1] )
            power_I1  = float( l[4][:-1] )
            power_I2  = float( l[5][:-1] )

            return SAgent_BatteryState( PowerType, S_V, L_V, power_U, power_I1, power_I2 )
        except:
            print( f"{SC.sWarning} {cls.__name__} can't construct from string '{data}', using default value '{cls.defVal()}'!" )
            return cls.defVal()

    def toString( self ):
        return f"{ EAgentBattery_Type.toString( self.PowerType ) }{DS}{self.S_V:.2f}V{DS}{self.L_V:.2f}V{DS}{self.power_U:.2f}V{DS}{self.power_I1:.2f}A{DS}{self.power_I2:.2f}A"

#########################################################
class SHW_Data:
    "cartV1^555"
    def __init__( self, agentType, agentN ):
        self.agentType = agentType
        self.agentN    = agentN
        self.bIsValid  = True

    def __str__( self ): return self.toString()

    @classmethod
    def fromString( cls, data ):
        l = data.split( DS )

        try:
            agentType = l[0]
            agentN    = int(l[1])
            bIsValid = True
        except:
            agentType = "Unknown Agent"
            agentN    = 0
            bIsValid = False

        HW_Data = SHW_Data( agentType, agentN )
        HW_Data.bIsValid = bIsValid

        return HW_Data

    def toString( self ):
        return f"{self.agentType}{ DS }{self.agentN:03d}"

#########################################################

class SOD_OP_Data:
    "OD~100"
    "OP~138"
    "OP~U"

    def __init__( self, bUndefined=True, nDistance=0 ):
        self.bUndefined = bUndefined
        self.nDistance = nDistance

    def __str__( self ): return self.toString()

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

#########################################################

class SNT_Data:
    "NT^ID"
    def __init__(self, event, data=None):
        self.event = event
        self.data = data

    def __str__( self ): return self.toString()

    @classmethod
    def fromString( cls, data ):
        l = data.split( DS )
        event = AEV.fromStr( l[0] )
        if len(l) > 1:
            data = f"{DS}".join( l[1::] )
        else:
            data = None
        
        return SNT_Data( event, data )

    def toString( self ):
        sResult = self.event.toStr()

        if self.data is not None:
            sResult += f"{ DS }{self.data}"

        return sResult
