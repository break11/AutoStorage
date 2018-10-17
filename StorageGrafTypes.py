
import enum

(
gaWidthType,
gaEdgeSize,
gaHighRailSizeFrom,
gaHighRailSizeTo,
gaCurvature,
gaEdgeType,
gaSensorSide,
gaChargeSide,
gaContainsAgent,
gaFloor_num,
gaX,
gaY,
gaNodeType,
gaStorageType,
gaName
) = range(15)

__GrafAttrsFromString = {
    "widthType"        : gaWidthType,
    "edgeSize"         : gaEdgeSize,
    "highRailSizeFrom" : gaHighRailSizeFrom,
    "highRailSizeTo"   : gaHighRailSizeTo,
    "curvature"        : gaCurvature,
    "edgeType"         : gaEdgeType,
    "sensorSide"       : gaSensorSide,
    "chargeSide"       : gaChargeSide,
    "containsAgent"    : gaContainsAgent,
    "floor_num"        : gaFloor_num,
    "x"                : gaX,
    "y"                : gaY,
    "nodeType"         : gaNodeType,
    "storageType"      : gaStorageType,
    "name"             : gaName
}

__GrafAttrsToString = {
    gaWidthType        : "widthType"
}

# sWidthType = gaToString[ gaWidthType ]
# gasX = gaToString( gaX )

graphAttrTypes = { gaWidthType        : str,
                   gaEdgeSize         : int,
                   gaHighRailSizeFrom : int,
                   gaHighRailSizeTo   : int,
                   gaCurvature        : str,
                   gaEdgeType         : str,
                   gaSensorSide       : str,
                   gaChargeSide       : str,
                   gaContainsAgent    : int,
                   gaFloor_num        : int,
                   gaX                : int,
                   gaY                : int,
                   gaNodeType         : str,
                   gaStorageType      : str,
                   gaName             : str
}

def adjustAttrType( sAttrName, val ):
    if val is None: return None
    val = (graphAttrTypes[ __GrafAttrsFromString[ sAttrName ] ] )( val )
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
