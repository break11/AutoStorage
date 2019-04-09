
from enum import Enum, auto
from PyQt5.QtCore import (Qt)

_graphAttrs = [
            "widthType",
            "edgeSize",
            "highRailSizeFrom",
            "highRailSizeTo",
            "curvature",
            "edgeType",
            "sensorSide",
            "chargeSide",
            "containsAgent",
            "floor_num",
            "x",
            "y",
            "nodeType",
            "storageType",
          ]

# Экспортируем "короткие" алиасы строковых констант
for str_item in _graphAttrs:
    locals()[ "s_" + str_item ] = str_item

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

