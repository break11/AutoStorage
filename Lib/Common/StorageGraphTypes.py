
from enum import Enum, auto
from PyQt5.QtCore import (Qt)
import Lib.Common.StrConsts as SC

_graphAttrs = [
            "widthType",
            "edgeSize",
            "highRailSizeFrom",
            "highRailSizeTo",
            "curvature",
            "sensorSide",
            "chargeSide",
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

    def fromString( sType ):
        try:
            widthType = EWidthType[ sType ]
        except:
            print( f"{SC.sWarning} Unknown edge width type ={sType}, using Narrow!" )
            widthType = EWidthType.Narrow
        return widthType

sensorNarr = 342  # half of distance between sensors (x axis)
sensorWide = 200  # half of distance between sensors (y axis)

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

    def fromString( sType ):
        try:
            curv = ECurvature[ sType ]
        except:
            print( f"{SC.sWarning} Unknown edge curvature ={sType}, using Straight!" )
            curv = ECurvature.Straight
        return curv

class ESensorSide( Enum ):
    SLeft    = auto()
    SRight   = auto()
    SBoth    = auto()
    SPassive = auto()

