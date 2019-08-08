
from enum import auto
import math
from PyQt5.QtCore import (Qt)

from .BaseEnum import BaseEnum

_graphAttrs = [
            "widthType",
            "edgeSize",
            "highRailSizeFrom",
            "highRailSizeTo",
            "curvature",
            "sensorSide",
            "chargeSide",
            "chargePort",
            "x",
            "y",
            "nodeType",
          ]

# Экспортируем "короткие" алиасы строковых констант
for str_item in _graphAttrs:
    locals()[ "s_" + str_item ] = str_item

#######################################################

class ENodeTypes( BaseEnum ):
    UnknownType    = auto()
    DummyNode      = auto()
    StorageSingle  = auto()
    Cross          = auto()
    PickStation    = auto()
    PickStationIn  = auto()
    PickStationOut = auto()
    ServiceStation = auto()
    Terminal       = auto()

    Default = UnknownType

nodeColors = {
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
    
class EWidthType( BaseEnum ):
    Narrow  = auto()
    Wide    = auto()

    Default = Narrow

sensorNarr = 342  # half of distance between sensors (x axis)
sensorWide = 200  # half of distance between sensors (y axis)

narrow_Rail_Width = 690
wide_Rail_Width   = 1140

railWidth = { EWidthType.Narrow : narrow_Rail_Width,
              EWidthType.Wide   : wide_Rail_Width
            }

###########################################################

class ECurvature( BaseEnum ):
    Curve    = auto()
    Straight = auto()

    Default = Straight

class ESensorSide( BaseEnum ):
    SLeft    = auto()
    SRight   = auto()
    SBoth    = auto()
    SPassive = auto()

    Default  = SBoth

class EDirection( BaseEnum ):
    Forward = auto()
    Rear    = auto()
    F       = Forward
    R       = Rear
    Error   = auto()

    Default = Error

class ESide( BaseEnum ):
    Left            = auto()
    Right           = auto()

    Default = Right

    @staticmethod
    def fromAngle( angle ):
        angle = angle % 360

        if angle > 45 and angle < 225:
            return ESide.Left
        else:
            return ESide.Right

graphEnums = { s_nodeType   : ENodeTypes,  #type:ignore
               s_sensorSide : ESensorSide, #type:ignore
               s_widthType  : EWidthType,  #type:ignore
               s_curvature  : ECurvature,  #type:ignore
               s_chargeSide : ESide,       #type:ignore
             }

def prepareGraphProps( nxGraph, bToEnum = True ):
    keys = graphEnums.keys()

    def prepareDict( props, bToEnum ):
        for k,v in props.items():
            if k in keys:
                if bToEnum:
                    props[ k ] = graphEnums[ k ].fromString( v )
                else:
                    props[ k ] = str( v )

    prepareDict( nxGraph.graph, bToEnum )

    for nodeProps in nxGraph.nodes().values():
        prepareDict( nodeProps, bToEnum )

    for edgeProps in nxGraph.edges().values():
        prepareDict( edgeProps, bToEnum )

default_Edge_Props = {
                        s_edgeSize:         500,                 # type: ignore
                        s_highRailSizeFrom: 0,                   # type: ignore
                        s_highRailSizeTo:   0,                   # type: ignore
                        s_sensorSide:       ESensorSide.SBoth,   # type: ignore
                        s_widthType:        EWidthType.Narrow,   # type: ignore
                        s_curvature:        ECurvature.Straight  # type: ignore
                    }

default_Node_Props = {  
                        s_x: 0,                                  # type: ignore
                        s_y: 0,                                  # type: ignore
                        s_nodeType: ENodeTypes.DummyNode,        # type: ignore
                    }
