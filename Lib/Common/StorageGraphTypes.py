
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

def _EnumFromString( enum, sValue, defValue ):
        try:
            rVal = enum[ sValue ]
        except:
            print( f"{SC.sWarning} Enum {enum} doesn't contain value for string = {sValue}, using {defValue.name}!" )
            rVal = defValue
        return rVal
    
class EWidthType( Enum ):
    Narrow = auto()
    Wide   = auto()

    @staticmethod
    def fromString( sType ): return _EnumFromString( EWidthType, sType, EWidthType.Narrow )

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

    @staticmethod
    def fromString( sType ): return _EnumFromString( ECurvature, sType, ECurvature.Straight )

class ESensorSide( Enum ):
    SLeft    = auto()
    SRight   = auto()
    SBoth    = auto()
    SPassive = auto()

    @staticmethod
    def fromString( sType ): return _EnumFromString( ESensorSide, sType, ESensorSide.SBoth )

class EDirection( Enum ):
    Forward = auto()
    Rear    = auto()
    F       = Forward
    R       = Rear
    Error   = auto()

    @staticmethod
    def fromString( sType ): return _EnumFromString( EDirection, sType, ESensorSide.Error )
