
from enum import auto
import math
from PyQt5.QtCore import Qt

from .BaseEnum import BaseEnum
from .Utils import СStrProps_Meta

class SGraphAttrs( metaclass = СStrProps_Meta ):
    widthType        = None
    edgeSize         = None
    highRailSizeFrom = None
    highRailSizeTo   = None
    curvature        = None
    sensorSide       = None
    chargeSide       = None
    chargePort       = None
    x                = None
    y                = None
    nodeType         = None

SGA = SGraphAttrs

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

    @classmethod
    def fromChar( cls, side_char ):
        sideFromData = { "L": "Left", "R": "Right" }
        return cls.fromString( sideFromData.get( side_char ) )

    def toChar(self):
        return self.toString()[0]

graphEnums = { SGA.nodeType   : ENodeTypes, 
               SGA.sensorSide : ESensorSide,
               SGA.widthType  : EWidthType, 
               SGA.curvature  : ECurvature, 
               SGA.chargeSide : ESide,      
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
                        SGA.edgeSize:         500,               
                        SGA.highRailSizeFrom: 0,                 
                        SGA.highRailSizeTo:   0,                 
                        SGA.sensorSide:       ESensorSide.SBoth, 
                        SGA.widthType:        EWidthType.Narrow, 
                        SGA.curvature:        ECurvature.Straight
                    }

default_Node_Props = {  
                        SGA.x: 0,                          
                        SGA.y: 0,                          
                        SGA.nodeType: ENodeTypes.DummyNode,
                    }
