
from enum import *

class EGrafAttrs( Enum ):
    widthType        = auto()
    edgeSize         = auto()
    highRailSizeFrom = auto()
    highRailSizeTo   = auto()
    curvature        = auto()
    edgeType         = auto()
    sensorSide       = auto()
    chargeSide       = auto()
    containsAgent    = auto()
    floor_num        = auto()
    x                = auto()
    y                = auto()
    nodeType         = auto()
    storageType      = auto()
    # name            = auto() # не используем из-за конфликта со встроенными атрибутами класса, нужен только в пропертях графа


graphAttrTypes = { EGrafAttrs.widthType        : str,
                   EGrafAttrs.edgeSize         : int,
                   EGrafAttrs.highRailSizeFrom : int,
                   EGrafAttrs.highRailSizeTo   : int,
                   EGrafAttrs.curvature        : str,
                   EGrafAttrs.edgeType         : str,
                   EGrafAttrs.sensorSide       : str,
                   EGrafAttrs.chargeSide       : str,
                   EGrafAttrs.containsAgent    : int,
                   EGrafAttrs.floor_num        : int,
                   EGrafAttrs.x                : int,
                   EGrafAttrs.y                : int,
                   EGrafAttrs.nodeType         : str,
                   EGrafAttrs.storageType      : str,
                #    GrafAttrs.name             : str,
}

def adjustAttrType( sAttrName, val ):
    if val is None: return None
    val = (graphAttrTypes[ EGrafAttrs[sAttrName] ] )( val )
    return val

#######################################################

(
ntDummyNode,
ntStorageSingle,
ntCross,
ntPickStation,
ntPickStationIn,
ntPickStationOut,
ntServiceStation,
ntTerminal
) = range(8)

__nodeTypeFromString = { "DummyNode"      : ntDummyNode,
                         "StorageSingle"  : ntStorageSingle,
                         "Cross"          : ntCross,
                         "Pickstation"    : ntPickStation,
                         "PickstationIn"  : ntPickStationIn,
                         "PickstationOut" : ntPickStationOut,
                         "ServiceStation" : ntServiceStation,
                         "Terminal"       : ntTerminal }

def ntFromString( sVal ) : return __nodeTypeFromString[ sVal ]
