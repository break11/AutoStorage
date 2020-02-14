
from enum import auto
import math
import re
from PyQt5.QtCore import Qt

from Lib.Common.BaseEnum import BaseEnum
from Lib.Common.StrProps_Meta import СStrProps_Meta
from Lib.Common.StrConsts import genSplitPattern
from Lib.Common.StrConsts import SC

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
    edgeType         = None
    linkLeft         = None
    linkRight        = None
    linkPlace        = None
    tsName           = None

SGA = SGraphAttrs

#######################################################

class ENodeTypes( BaseEnum ):
    DummyNode        = auto()
    RailPoint        = auto()
    StoragePoint     = auto()
    RailCross        = auto()
    PickStation      = auto()
    PowerStation     = auto()
    Terminal         = auto()
    TransporterPoint = auto()
    TP               = TransporterPoint
    UserPoint        = auto()

    Undefined = auto()
    Default   = DummyNode

nodeColors = {
    ENodeTypes.Undefined        : Qt.darkRed,
    ENodeTypes.DummyNode        : Qt.darkRed,
    ENodeTypes.RailPoint        : Qt.darkGreen,
    ENodeTypes.StoragePoint     : Qt.cyan,
    ENodeTypes.RailCross        : Qt.darkMagenta,
    ENodeTypes.PickStation      : Qt.darkYellow,
    ENodeTypes.PowerStation     : Qt.darkBlue,
    ENodeTypes.Terminal         : Qt.lightGray,
    ENodeTypes.TransporterPoint : Qt.darkRed,
    ENodeTypes.UserPoint        : Qt.darkCyan,
}

#######################################################
class EEdgeTypes( BaseEnum ):
    Rail        = auto()
    Transporter = auto()

    Undefined = auto()
    Default = Rail

#######################################################
class ERailHeight( BaseEnum ):
    High = auto()
    Low  = auto()
    H = High
    L = Low

    Undefined = auto()
    Default = Low

#######################################################
                           
class EWidthType( BaseEnum ):
    Narrow  = auto()
    Wide    = auto()
    # сокращенные элементы для работы fromString по ним
    N = Narrow
    W = Wide

    Undefined = auto()
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
    # сокращенные элементы для работы fromString по ним
    C = Curve
    S = Straight

    Undefined = auto()
    Default = Straight

class ESensorSide( BaseEnum ):
    SLeft    = auto()
    SRight   = auto()
    SBoth    = auto()
    SPassive = auto()
    # сокращенные элементы для работы fromString по ним
    L = SLeft
    R = SRight
    B = SBoth
    P = SPassive

    Undefined = auto()
    Default   = SBoth

    def shortName( self ): return self.name[1] # SLeft = L, SRight = R

class EDirection( BaseEnum ):
    Forward = auto()
    Rear    = auto()
    Error   = auto()
    # сокращенные элементы для работы fromString по ним
    F = Forward
    R = Rear

    Undefined = auto()
    Default = Forward

class ESide( BaseEnum ):
    Left      = auto()
    Right     = auto()
    # сокращенные элементы для работы fromString по ним
    L         = Left
    R         = Right

    Undefined = auto()
    U         = Undefined
    Default   = Right

    @staticmethod
    def fromAngle( angle ):
        angle = angle % 360

        if angle > 45 and angle <= 225:
            return ESide.Left
        else:
            return ESide.Right

    def invert(self):
        assert self != ESide.Undefined, "Func 'invert()' can invert only 'Left' or 'Rigth' values!"
        return ESide.Left if self == ESide.Right else ESide.Right

###########################################################

class SNodePlace:
    DS = "|"
    DS_split_pattern = genSplitPattern( f"\{DS}" )

    def __init__( self, nodeID, side ):
        self.nodeID = nodeID
        self.side = side

    def __str__( self ): return self.toString()

    def isValid( self ): return self.nodeID and ( self.side != ESide.Undefined )

    def __eq__( self, other ):
        eq = True
        eq = eq and self.nodeID == other.nodeID
        eq = eq and self.side == other.side
        return eq

    @classmethod
    def fromString( cls, data ):
        l = re.split( cls.DS_split_pattern, data )

        try:
            nodeID = l[0]
            side   = ESide.fromString( l[1] )
        except:
            print( f"{SC.sWarning} SNodePlace can't convert from '{data}'!" )
            nodeID = ""
            side   = ESide.Undefined

        return SNodePlace( nodeID = nodeID, side = side )

    def toString( self ): return f"{self.nodeID}{ self.DS }{self.side}"

###########################################################

class SEdgePlace:
    DS = "|"
    DS_split_pattern = genSplitPattern( f"\{DS}" )

    def __init__( self, nodeID_1, nodeID_2, pos ):
        self.nodeID_1 = nodeID_1
        self.nodeID_2 = nodeID_2
        self.pos = pos

    def __str__( self ): return self.toString()

    def isValid( self ): return self.nodeID_1 and self.nodeID_2 and ( self.pos is not None )

    def __eq__( self, other ):
        eq = True
        eq = eq and self.nodeID_1 == other.nodeID_1
        eq = eq and self.nodeID_2 == other.nodeID_2
        eq = eq and self.pos == other.pos
        return eq

    @classmethod
    def fromString( cls, data ):
        l = re.split( cls.DS_split_pattern, data )

        try:
            nodeID_1 = l[0]
            nodeID_1 = l[1]
            pos      = int( l[3] )
        except:
            print( f"{SC.sWarning} SEdgePlace can't convert from '{data}'!" )
            nodeID_1 = ""
            nodeID_2 = ""
            pos      = None

        return SEdgePlace( nodeID_1, nodeID_2, pos )

    def toString( self ): return f"{self.nodeID_1}{ self.DS }{self.nodeID_2}{ self.DS }{self.pos}"

###########################################################

graphEnums = { SGA.nodeType   : ENodeTypes, 
               SGA.edgeType   : EEdgeTypes,
               SGA.sensorSide : ESensorSide,
               SGA.widthType  : EWidthType, 
               SGA.curvature  : ECurvature, 
               SGA.chargeSide : ESide,
               SGA.linkLeft   : SNodePlace,
               SGA.linkRight  : SNodePlace,
               SGA.linkPlace  : SNodePlace
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
