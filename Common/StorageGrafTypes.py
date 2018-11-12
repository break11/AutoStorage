
from enum import *
from PyQt5.QtCore import (Qt)

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

# Экспортируем "короткие" алиасы имен атрибутов ( будет доступно по SGT.s_nodeType, SGT.s_x и т.д. )
for attr in EGrafAttrs:
    locals()[ "s_" + attr.name ] = attr.name

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
                #    EGrafAttrs.name             : str,
}

def adjustAttrType( sAttrName, val ):
    if val is None: return None

    # для атрибутов, которых нет в списке возвращаем без преобразования типа
    if not EGrafAttrs.__members__.get( sAttrName ): return val
    
    val = (graphAttrTypes[ EGrafAttrs[sAttrName] ] )( val )
    return val

#######################################################

class ENodeTypes( Enum ):
    DummyNode      = auto()
    StorageSingle  = auto()
    Cross          = auto()
    PickStation    = auto()
    PickStationIn  = auto()
    PickStationOut = auto()
    ServiceStation = auto()
    Terminal       = auto()

nodeColors = {
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

railWidth = {
    EWidthType.Narrow.name : 690,
    EWidthType.Wide.name   : 1140,
    None                   : 690,
}

class ECurvature( Enum ):
    Curve    = auto()
    Straight = auto()

class ESensorSide( Enum ):
    SLeft    = auto()
    SRight   = auto()
    SBoth    = auto()
    SPassive = auto()
