from enum import Enum
from Lib.Common.StrConsts import SC

class BaseEnum( Enum ):
    @classmethod
    def fromString( cls, sValue ): return EnumFromString( cls, sValue = sValue, defValue = cls.Undefined )

    def toString( self, bShortForm = False ):
        if not bShortForm:
            return EnumToString( self )
        else:
            return self.shortName()

    def __str__( self ): return self.toString()

    def shortName( self ): return self.name[0]

def EnumFromString( enum, sValue, defValue ):
    try:
        rVal = enum[ sValue ]
    except KeyError as e:
        print( f"{SC.sWarning} Enum {enum} doesn't contain value for val = {sValue} of type = {type(sValue)}, using {defValue}!" )
        rVal = defValue
    return rVal

def EnumToString( enumValue ):
    return enumValue.name
