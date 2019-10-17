
from enum import auto, IntEnum
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
class ERailHeight( IntEnum ):
    H = 1
    L = 0
    High = H
    Low  = L

#######################################################
                           
class EWidthType( BaseEnum ):
    Narrow  = auto()
    Wide    = auto()
    # сокращенные элементы для работы fromString по ним
    N = Narrow
    W = Wide

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

    def shortName( self ): return self.name[1] # SLeft = L, SRight = R

class EDirection( BaseEnum ):
    Forward = auto()
    Rear    = auto()
    Error   = auto()

    Default = Error

class ESide( BaseEnum ):
    Left    = auto()
    Right   = auto()
    L       = Left
    R       = Right

    Default = Right

    @staticmethod
    def fromAngle( angle ):
        angle = angle % 360

        if angle > 45 and angle < 225:
            return ESide.Left
        else:
            return ESide.Right

    def invert(self):
        return ESide.Left if self == ESide.Right else ESide.Right

###########################################################

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
