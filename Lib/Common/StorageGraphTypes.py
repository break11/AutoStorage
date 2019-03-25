
from enum import Enum, auto
from PyQt5.QtCore import (Qt)

class EGraphAttrs( Enum ):
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

# Экспортируем "короткие" алиасы имен атрибутов ( будет доступно по SGT.s_nodeType, SGT.s_x и т.д. )
for attr in EGraphAttrs:
    locals()[ "s_" + attr.name ] = attr.name

graphAttrTypes = { EGraphAttrs.widthType        : str,
                   EGraphAttrs.edgeSize         : int,
                   EGraphAttrs.highRailSizeFrom : int,
                   EGraphAttrs.highRailSizeTo   : int,
                   EGraphAttrs.curvature        : str,
                   EGraphAttrs.edgeType         : str,
                   EGraphAttrs.sensorSide       : str,
                   EGraphAttrs.chargeSide       : str,
                   EGraphAttrs.containsAgent    : int,
                   EGraphAttrs.floor_num        : int,
                   EGraphAttrs.x                : int,
                   EGraphAttrs.y                : int,
                   EGraphAttrs.nodeType         : str,
                   EGraphAttrs.storageType      : str,
                #    EGraphAttrs.name             : str,
}

def adjustAttrType( sAttrName, val ):
    if val is None: return None

    # для атрибутов, которых нет в списке возвращаем без преобразования типа
    if not EGraphAttrs.__members__.get( sAttrName ): return val
    
    val = (graphAttrTypes[ EGraphAttrs[sAttrName] ] )( val )
    return val

#######################################################

class ENodeTypes( Enum ):
    NoneType       = auto()
    UnknownType    = auto()
    DummyNode      = auto()
    StorageSingle  = auto()
    Cross          = auto()
    PickStation    = auto()
    PickStationIn  = auto()
    PickStationOut = auto()
    ServiceStation = auto()
    Terminal       = auto()

nodeColors = {
    ENodeTypes.NoneType       : Qt.darkGray,
    ENodeTypes.UnknownType    : Qt.darkRed,
    ENodeTypes.DummyNode      : Qt.darkGreen,
    ENodeTypes.StorageSingle  : Qt.cyan,
    ENodeTypes.Cross          : Qt.darkMagenta,
    ENodeTypes.PickStation    : Qt.blue,
    ENodeTypes.PickStationIn  : Qt.darkYellow,
    ENodeTypes.PickStationOut : Qt.yellow,
    ENodeTypes.ServiceStation : Qt.darkBlue,
    ENodeTypes.Terminal       : Qt.lightGray,
}

#######################################################

class EWidthType( Enum ):
    Narrow = auto()
    Wide   = auto()

def railType( sType ):
    try:
        railType = EWidthType[ sType ]
    except:
        railType = EWidthType.Narrow
    return railType

narrow_Rail_Width = 690
wide_Rail_Width   = 1140

__railWidth = {
    EWidthType.Narrow.name : narrow_Rail_Width,
    EWidthType.Wide.name   : wide_Rail_Width
}

def railWidth( sWidthType ):
    try:
        return __railWidth[ sWidthType ]
    except KeyError:
        return narrow_Rail_Width

###########################################################

class ECurvature( Enum ):
    Curve    = auto()
    Straight = auto()

class ESensorSide( Enum ):
    SLeft    = auto()
    SRight   = auto()
    SBoth    = auto()
    SPassive = auto()

def adjustGraphPropsDict( d ):
    d1 = {}
    for k,v in d.items():
        k1 = k.decode() 
        v1 = v.decode()
        d1[ k1 ] = adjustAttrType( k1, v1 )
    return d1

