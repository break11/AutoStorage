
from enum import auto
import re

from Lib.Common.StrConsts import SC, genSplitPattern
from Lib.Common.BaseEnum import BaseEnum

class EConnectionType( BaseEnum ):
    TCP_IP = auto()
    USB    = auto()

    Undefined = auto()
    Default   = TCP_IP

################################

class SIPAddress:
    DS = ":"
    "127.0.0.1:5020"
    
    def __init__( self, address, port, bValid = True ):
        self.address = address
        self.port    = port
        self.bValid  = bValid

    def __str__( self ): return self.toString()

    def __eq__( self, other ):
        eq = True
        eq = eq and self.address == other.address
        eq = eq and self.port == other.port
        eq = eq and self.bValid == other.bValid

    @classmethod
    def fromString( cls, data ):
        l = data.split( cls.DS )
        try:
            address = l[0]
            port = int( l[1] )
            bValid = True
        except:
            address = SC.localhost
            port = 8888
            bValid = False

        return SIPAddress( address, port, bValid )

    def toString( self, bShortForm = False ):
        sResult = f"{self.address}{ self.DS }{self.port}"

        return sResult

################################

MDS = "="
MDS_split_pattern = genSplitPattern( MDS )

class CСompositeType:
    # Some Enum = Some Data ( diff data by enum values )
    def __init__( self, _type, data = None ):
        self._type = _type

        if _type != self.baseType.Undefined:
            dataType = self.dataType_by_BaseType.get( _type )
            assert dataType == type(data), "Data type of connection invalid!"
            
        self.data = data

    def __str__( self ): return self.toString()

    def __eq__( self, other ):
        eq = True
        eq = eq and self._type == other._type
        eq = eq and self.data == other.data

        return eq

    @classmethod
    def fromString( cls, data ):
        l = re.split( MDS_split_pattern, data )
        _type = cls.baseType.fromString( l[0] )
        if len( l ) > 1:
            data = cls.dataFromString( _type, l[1] )
        else:
            data = None
        return cls( _type, data )

    def toString( self ):
        sR = f"{self._type}"
        if self.data:
            sR = f"{sR}{MDS}{self.data}"
        return sR

    @classmethod
    def dataFromString( cls, _type, sData ):
        try:
            return cls.dataFromStrFunc[ _type ]( sData )
        except:
            return None

################################

class CConnectionAddress( CСompositeType ):
    baseType = EConnectionType

    dataFromStrFunc = {
                        EConnectionType.Undefined : lambda sData : sData,
                        EConnectionType.USB       : lambda sData : sData,
                        EConnectionType.TCP_IP    : SIPAddress.fromString,
                      }

    dataType_by_BaseType = {
                            EConnectionType.USB    : str,
                            EConnectionType.TCP_IP : SIPAddress
                           }
