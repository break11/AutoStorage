from enum import auto
from Lib.Common.BaseEnum import BaseEnum
from Lib.Common.StrConsts import SC

class ERegisterType( BaseEnum ):
    DI = auto() # Discrete Input Contacts
    DO = auto() # Discrete Output Coils
    AI = auto() # Analog Input Registers
    AO = auto() # Analog Output Holding Registers

    Undefined = auto()
    Default   = DI

    DigitalInput  = DI
    DigitalOutput = DO
    AnalogInput   = AI
    AnalogOutput  = AO
    
ERT = ERegisterType

class CRegisterAddress:
    @classmethod
    def def_DI(cls): return cls.def_address( _type=ERegisterType.DI )
    @classmethod
    def def_DO(cls): return cls.def_address( _type=ERegisterType.DO )
    @classmethod
    def def_AI(cls): return cls.def_address( _type=ERegisterType.AI )
    @classmethod
    def def_AO(cls): return cls.def_address( _type=ERegisterType.AO )

    @classmethod
    def def_address( cls, _type=ERegisterType.DI, number=0, unitID=1 ): return CRegisterAddress( _type=_type, number=0, unitID=1 )

    DS = "|"
    # "1|AI|51"
    
    def __init__( self, unitID, _type, number, bitNum=None, bValid = True ):
        self.unitID = unitID
        self._type   = _type
        self.number = number
        self.bitNum = bitNum
        self.bValid  = bValid

    def __str__( self ): return self.toString()

    def __eq__( self, other ):
        eq = True
        eq = eq and self.unitID == other.unitID
        eq = eq and self._type == other._type
        eq = eq and self.number == other.number
        eq = eq and self.bitNum == other.bitNum
        eq = eq and self.bValid == other.bValid
        return eq

    @classmethod
    def fromString( cls, data ):
        l = data.split( cls.DS )
        try:
            unitID = int( l[0] )
            _type = ERegisterType.fromString( l[1] )
            number = int( l[2] )
            bitNum = int( l[3] ) if len( l ) > 3 else None
            bValid = True
        except:
            print( f"{SC.sError} CRegisterAddress can't convert from '{data}'!" )
            unitID = 0
            _type = ERegisterType.Undefined
            number = 0
            bitNum = 0
            bValid = False

        return CRegisterAddress( unitID, _type, number, bitNum, bValid )

    def toString( self, bShortForm = False ):
        sResult = f"{self.unitID}{ self.DS }{self._type}{ self.DS }{self.number}"
        if self.bitNum is not None:
            sResult += f"{ self.DS }{self.bitNum}"

        return sResult
