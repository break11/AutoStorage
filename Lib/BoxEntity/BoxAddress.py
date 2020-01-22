from enum import auto
import re

from Lib.Common.BaseEnum import BaseEnum
import Lib.GraphEntity.StorageGraphTypes as SGT
from Lib.Common.StrConsts import genSplitPattern

MDS = "="
MDS_split_pattern = genSplitPattern( MDS )

class EBoxAddressType( BaseEnum ):
    OnNode  = auto()
    OnAgent = auto()

    Undefined = auto()
    Default   = OnNode

class CBoxAddress:
    dataFromStrFunc = {
                        EBoxAddressType.Undefined : lambda sData : sData,
                        EBoxAddressType.OnNode    : SGT.SNodePlace.fromString,
                        EBoxAddressType.OnAgent   : lambda sData : int( sData ),
                      }

    def __init__( self, addressType, data = None ):
        self.addressType = addressType
        self.data = data

    def __str__( self ): return self.toString()

    def __eq__( self, other ):
        eq = True
        eq = eq and self.addressType == other.addressType
        eq = eq and self.data == other.data

        return eq

    @classmethod
    def fromString( cls, data ):
        l = re.split( MDS_split_pattern, data )
        addressType = EBoxAddressType.fromString( l[0] )
        if len( l ) > 1:
            data = cls.dataFromString( addressType, l[1] )
        else:
            data = None
        return CBoxAddress( addressType, data )

    def toString( self ):
        sR = f"{self.addressType}"
        if self.data:
            sR = f"{sR}{MDS}{self.data}"
        return sR

    @classmethod
    def dataFromString( cls, addressType, sData ):
        try:
            return cls.dataFromStrFunc[ addressType ]( sData )
        except:
            return None
