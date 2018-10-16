
graphML_attr_types = { "widthType"        : str,
                       "edgeSize"         : int,
                       "highRailSizeFrom" : int,
                       "highRailSizeTo"   : int,
                       "curvature"        : str,
                       "edgeType"         : str,
                       "sensorSide"       : str,
                       "chargeSide"       : str,
                       "containsAgent"    : int,
                       "floor_num"        : int,
                       "x"                : int,
                       "y"                : int,
                       "nodeType"         : str,
                       "storageType"      : str,
                       "name"             : str }

def adjustAttrType( sAttrName, val ):
    if val is None: return None
    val = (graphML_attr_types[ sAttrName ] )( val )
    return val

ntDummyNode, ntStorageSingle, ntCross, ntPickStation, ntPickStationIn, ntPickStationOut, ntServiceStation, ntTerminal = range(8)

__nodeType = { "DummyNode"      : ntDummyNode,
                "StorageSingle"  : ntStorageSingle,
                "Cross"          : ntCross,
                "Pickstation"    : ntPickStation,
                "PickstationIn"  : ntPickStationIn,
                "PickstationOut" : ntPickStationOut,
                "ServiceStation" : ntServiceStation,
                "Terminal"       : ntTerminal }

def ntFromString( sVal ) : return __nodeType[ sVal ]
