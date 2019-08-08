from enum import Enum
import Lib.Common.StrConsts as SC

class BaseEnum( Enum ):
    @classmethod
    def fromString( cls, sType ): return EnumFromString( cls, sType, cls.Default )

    def toString( self ): return EnumToString( self )

    def __str__( self ): return self.toString()

def EnumFromString( enum, sValue, defValue ):
    try:
        rVal = enum[ sValue ]
    except KeyError as e:
        print( f"{SC.sWarning} Enum {enum} doesn't contain value for val = {sValue} of type = {type(sValue)}, using {defValue}!" )
        rVal = defValue
    return rVal

def EnumToString( enumValue ):
    return enumValue.name
