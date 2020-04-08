
from enum import auto
import re

from Lib.Common.StrConsts import SC, genSplitPattern
from Lib.Common.BaseEnum import BaseEnum

class EConnectionType( BaseEnum ):
    TCP_IP = auto()
    USB    = auto()

    Undefined = auto()
    Default   = TCP_IP

    tcp = TCP_IP
    usb = USB

################################

class SIPAddress:
    DS = "|"
    # "127.0.0.1|1111"
    
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
        return eq

    @classmethod
    def fromString( cls, data ):
        l = data.split( cls.DS )
        try:
            address = l[0]
            port = int( l[1] )
            bValid = True
        except:
            print( f"{SC.sError} SIPAddress can't convert from '{data}'!" )
            address = SC.localhost
            port = 1111
            bValid = False

        return SIPAddress( address, port, bValid )

    def toString( self ):
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
            assert dataType == type(data), f"Received data type { type(data) } not equal with expected data type { dataType } for enum value {_type} of {self.__class__.__name__}!"
            
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
            data = cls.dataFromString( _type, "" )
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
    @classmethod
    def defTCP_IP(cls): return CConnectionAddress( _type=EConnectionType.TCP_IP, data=SIPAddress( address="127.0.0.1", port=8888 ) )

    @classmethod
    def TCP_IP(cls, ip_address, port): return CConnectionAddress( _type=EConnectionType.TCP_IP, data=SIPAddress( address=ip_address, port=port ) )

    @classmethod
    def USB(cls, sDevFName): return CConnectionAddress( _type=EConnectionType.USB, data=sDevFName )

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
