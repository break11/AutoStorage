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

class CRegisterAddress:
    DS = "|"
    # "1|AI|51"
    
    def __init__( self, unitID, _type, number, bValid = True ):
        self.unitID = unitID
        self._type   = _type
        self.number = number
        self.bValid  = bValid

    def __str__( self ): return self.toString()

    def __eq__( self, other ):
        eq = True
        eq = eq and self.unitID == other.unitID
        eq = eq and self.type == other.type
        eq = eq and self.number == other.number
        eq = eq and self.bValid == other.bValid
        return eq

    @classmethod
    def fromString( cls, data ):
        l = data.split( cls.DS )
        try:
            unitID = int( l[0] )
            _type = ERegisterType.fromString( l[1] )
            number = int( l[2] )
            bValid = True
        except:
            print( f"{SC.sError} CRegisterAddress can't convert from '{data}'!" )
            unitID = 0
            if _type is None:
                _type = ERegisterType.Default
            number = 0
            bValid = False

        return CRegisterAddress( unitID, _type, number, bValid )

    def toString( self, bShortForm = False ):
        sResult = f"{self.unitID}{ self.DS }{self._type}{ self.DS }{self.number}"

        return sResult
