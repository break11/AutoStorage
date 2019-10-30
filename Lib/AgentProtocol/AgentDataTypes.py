
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

# хелперная функция для принудительного перевода данных команды в строку, независимо от исходного типа
def agentDataToStr( data, bShortForm = False ):
    if data is None:
        return ""
    elif type(data) == str:
        return data
    else:
        return data.toString( bShortForm=bShortForm )

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

    BoxLoad_Right   = auto()
    BoxLoad_Left    = auto()
    BoxUnload_Right = auto()
    BoxUnload_Left  = auto()

    NoRouteToCharge = auto() # не найден маршрут к зарядке - зарядки нет на графе или неправильный угол челнока 
    PosSyncError    = auto() # ошибка синхронизации по графу - несоответствие реального положения челнока и положения в программе
    CantCharge      = auto() # нет свойства с именем chargePort в ноде зарядки
    AgentError      = auto() # пришла ошибка с тележки
    RouteError      = auto() # не загружен граф, в маршруте указаны несуществующие точки, грани

    Default         = Idle

errorStatuses = [ EAgent_Status.NoRouteToCharge,
                  EAgent_Status.PosSyncError,
                  EAgent_Status.CantCharge,
                  EAgent_Status.AgentError,
                  EAgent_Status.RouteError ]

BL_BU_Agent_Status = { (AEV.BoxLoad,   SGT.ESide.Left)  : EAgent_Status.BoxLoad_Left,
                       (AEV.BoxLoad,   SGT.ESide.Right) : EAgent_Status.BoxLoad_Right,
                       (AEV.BoxUnload, SGT.ESide.Left)  : EAgent_Status.BoxUnload_Left,
                       (AEV.BoxUnload, SGT.ESide.Right) : EAgent_Status.BoxUnload_Right,
                    }

BL_BU_Agent_Status_vals = BL_BU_Agent_Status.values()

#########################################################

# базовый класс для некоторых типов данных команд - нужен для убирания повторяемого кода
# в наследниках нужна реализация _fromString - внутри которой не обрабытываются исключения
# должно быть поле класса sDefVal - с дефолтным значением, на случай, если пришло невалидное значение, которое нельзя распознать из строки
class СBaseDataType:
    @classmethod
    def defVal( cls ): return cls.fromString( cls.sDefVal )

    def __str__( self ): return self.toString()

    @classmethod
    def fromString( cls, data ):
        try:
            return cls._fromString( data )
        except Exception as e:
            print( f"Exception: {e}'!" )
            val = cls.defVal()
            val.bUsingDefaultValue = True
            print( f"{SC.sWarning} {cls.__name__} can't construct from string '{data}', using default value '{val}'!" )
            return val

#########################################################

class EAgentBattery_Type( BaseEnum ):
    Supercap   = auto()
    Li         = auto()
    NoPower    = auto()
    # сокращенные элементы для работы fromString по ним
    S = Supercap
    L = Li
    N = NoPower

    Default    = Supercap
    
#########################################################

class SBS_Data( СBaseDataType ):
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

    def supercapPercentCharge( self ):
        E = 0.5 * self.C * (self.S_V ** 2)
        return 100 * ( max(E - self.E_empty, 0) ) / ( self.E_full - self.E_empty )

    @classmethod
    def _fromString( cls, data ):
        l = data.split( DS )
        
        PowerType = EAgentBattery_Type.fromString( l[0] )
        S_V       = float( l[1][:-1] )
        L_V       = float( l[2][:-1] )
        power_U   = float( l[3][:-1] )
        power_I1  = float( l[4][:-1] )
        power_I2  = float( l[5][:-1] )

        return SBS_Data( PowerType, S_V, L_V, power_U, power_I1, power_I2 )

    def toString( self, bShortForm = False ):
        return f"{ self.PowerType.toString( bShortForm=bShortForm ) }{DS}"\
               f"{self.S_V:.2f}V{DS}{self.L_V:.2f}V{DS}{self.power_U:.2f}V{DS}{self.power_I1:.2f}A{DS}{self.power_I2:.2f}A"

#########################################################

class STS_Data( СBaseDataType ):
    sDefVal = f"24{DS}29{DS}29{DS}29{DS}29{DS}25{DS}25{DS}25{DS}25"
    def __init__( self, powerSource, 
                        wheelDriver_0, wheelDriver_1, wheelDriver_2, wheelDriver_3,
                        turnDriver_0, turnDriver_1, turnDriver_2, turnDriver_3 ):

        self.powerSource   = powerSource
        self.wheelDriver_0 = wheelDriver_0
        self.wheelDriver_1 = wheelDriver_1
        self.wheelDriver_2 = wheelDriver_2
        self.wheelDriver_3 = wheelDriver_3
        self.turnDriver_0  = turnDriver_0
        self.turnDriver_1  = turnDriver_1
        self.turnDriver_2  = turnDriver_2
        self.turnDriver_3  = turnDriver_3

    @classmethod
    def _fromString( cls, data ):
        l = data.split( DS )

        powerSource   = float( l[0] )
        wheelDriver_0 = float( l[1] )
        wheelDriver_1 = float( l[2] )
        wheelDriver_2 = float( l[3] )
        wheelDriver_3 = float( l[4] )
        turnDriver_0  = float( l[5] )
        turnDriver_1  = float( l[6] )
        turnDriver_2  = float( l[7] )
        turnDriver_3  = float( l[8] )

        return STS_Data( powerSource, wheelDriver_0, wheelDriver_1, wheelDriver_2, wheelDriver_3,
                                      turnDriver_0, turnDriver_1, turnDriver_2, turnDriver_3 )

    def toString( self, bShortForm = False ):
        return f"{self.powerSource  :.0f}{ DS }"\
               f"{self.wheelDriver_0:.0f}{ DS }"\
               f"{self.wheelDriver_1:.0f}{ DS }"\
               f"{self.wheelDriver_2:.0f}{ DS }"\
               f"{self.wheelDriver_3:.0f}{ DS }"\
               f"{self.turnDriver_0 :.0f}{ DS }"\
               f"{self.turnDriver_1 :.0f}{ DS }"\
               f"{self.turnDriver_2 :.0f}{ DS }"\
               f"{self.turnDriver_3 :.0f}"

#########################################################

class SDP_Data( СBaseDataType ):
    sDefVal = "000000^F^L^B^S"
    def __init__( self, length, direction, railHeight, sensorSide, curvature ):
        self.length     = length
        self.direction  = direction  # SGT.EDirection
        self.railHeight = railHeight # SGT.ERailHeight
        self.sensorSide = sensorSide # SGT.ESensorSide
        self.curvature  = curvature  # SGT.ECurvature

    def toString( self, bShortForm = False ):
        return f"{self.length:06d}{ DS }"\
               f"{self.direction.toString( bShortForm=bShortForm )}{ DS }"\
               f"{self.railHeight.toString( bShortForm=bShortForm )}{ DS }"\
               f"{self.sensorSide.toString( bShortForm=bShortForm )}{ DS }"\
               f"{self.curvature.toString( bShortForm=bShortForm )}"

    @classmethod
    def _fromString( cls, data ):
        l = data.split( DS )
        
        length     = int( l[0] )
        direction  = SGT.EDirection.fromString ( l[1] )
        railHeight = SGT.ERailHeight.fromString( l[2] )
        sensorSide = SGT.ESensorSide.fromString( l[3] )
        curvature  = SGT.ECurvature.fromString ( l[4] )

        return SDP_Data( length, direction, railHeight, sensorSide, curvature )

#########################################################

class SNT_Data( СBaseDataType ):
    sDefVal = "ID"
    def __init__(self, event, data=None):
        self.event = event
        self.data = data

    @classmethod
    def _fromString( cls, data ):
        l = data.split( DS )
        
        event = AEV.fromStr( l[0] )
        if event is None:
            event = AEV.Idle
        else:
            if len(l) > 1:
                data = f"{DS}".join( l[1::] )
                data = extractDT( event, data )
            else:
                data = None
        
        return SNT_Data( event, data )

    def toString( self, bShortForm = False ):
        sResult = self.event.toStr()

        if self.data is not None:
            sResult += f"{ DS }{self.data.toString( bShortForm=bShortForm )}"

        return sResult

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

    def toString( self, bShortForm = False ):
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

    def toString( self, bShortForm = False ):
        if not self.bUndefined:
            sResult = str( self.nDistance )
        else:
            sResult = "U"

        return sResult

#########################################################

DT_by_events = { AEV.BatteryState       : SBS_Data,
                 AEV.TemperatureState   : STS_Data,
                 AEV.OdometerDistance   : SOD_OP_Data,
                 AEV.OdometerPassed     : SOD_OP_Data,
                 AEV.HelloWorld         : SHW_Data,
                 AEV.NewTask            : SNT_Data,
                 AEV.WheelOrientation   : SGT.EWidthType,
                 AEV.DistancePassed     : SDP_Data,
                 AEV.BoxLoad            : SGT.ESide,
                 AEV.BoxUnload          : SGT.ESide,
               }

def extractDT( event, data ):
    dataType = DT_by_events.get( event )
    if dataType is None:
        return data
    else:
        return dataType.fromString( data )
