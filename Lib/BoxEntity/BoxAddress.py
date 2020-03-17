from enum import auto

from Lib.Common.BaseEnum import BaseEnum
from Lib.Common.BaseTypes import CСompositeType
import Lib.GraphEntity.StorageGraphTypes as SGT
from Lib.Common.StrConsts import genSplitPattern

MDS = "="
MDS_split_pattern = genSplitPattern( MDS )

class EBoxAddressType( BaseEnum ):
    OnNode  = auto()
    OnEdge  = auto()
    OnAgent = auto()

    Undefined = auto()
    Default   = OnNode

################################

class CBoxAddress( CСompositeType ):
    baseType = EBoxAddressType
    dataFromStrFunc = {
                        EBoxAddressType.Undefined : lambda sData : sData,
                        EBoxAddressType.OnNode    : SGT.SNodePlace.fromString,
                        EBoxAddressType.OnEdge    : SGT.SEdgePlace.fromString,
                        EBoxAddressType.OnAgent   : lambda sData : sData,
                      }

    dataType_by_BaseType = {
                            EBoxAddressType.OnNode    : SGT.SNodePlace,
                            EBoxAddressType.OnEdge    : SGT.SEdgePlace,
                            EBoxAddressType.OnAgent   : str
                           }
