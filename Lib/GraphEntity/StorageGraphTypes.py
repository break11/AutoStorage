
from enum import auto
import math
import re
from PyQt5.QtCore import Qt

from Lib.Common.BaseEnum import BaseEnum
from Lib.Common.StrProps_Meta import СStrProps_Meta
from Lib.Common.StrConsts import genSplitPattern, SC
import Lib.Common.BaseTypes as BT
import Lib.Modbus.ModbusTypes as MT
import Lib.PowerStationEntity.PowerStationTypes as PST

class SGraphAttrs( metaclass = СStrProps_Meta ):
    x                = None
    y                = None

    nodeType         = None
    edgeType         = None

    widthType        = None
    edgeSize         = None
    highRailSizeFrom = None
    highRailSizeTo   = None
    curvature        = None
    sensorSide       = None

    chargeSide       = None
    chargeAddress    = None
    chargeStage      = None
    powerState       = None

    linkLeft         = None
    linkRight        = None
    linkPlace        = None
    tsName           = None
    sensorAddress    = None
    sensorState      = None

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
    UserPoint        = auto()

    Undefined = auto()
    Default   = DummyNode

    TP               = TransporterPoint

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

    Undefined = auto()
    Default = Low

    H = High
    L = Low


#######################################################
                           
class EWidthType( BaseEnum ):
    Narrow  = auto()
    Wide    = auto()

    Undefined = auto()
    Default = Narrow

    # сокращенные элементы для работы fromString по ним
    N = Narrow
    W = Wide
    
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

    Undefined = auto()
    Default = Straight

    GetClose    = Curve
    NotGetClose = Straight
    # сокращенные элементы для работы fromString по ним
    C = Curve
    S = Straight


class ESensorSide( BaseEnum ):
    SLeft    = auto()
    SRight   = auto()
    SBoth    = auto()
    SPassive = auto()

    Undefined = auto()
    Default   = SBoth

    # сокращенные элементы для работы fromString по ним
    L = SLeft
    R = SRight
    B = SBoth
    P = SPassive

    def shortName( self ): return self.name[1] # SLeft = L, SRight = R

class EDirection( BaseEnum ):
    Forward = auto()
    Rear    = auto()
    Error   = auto()

    Undefined = auto()
    Default = Forward

    # сокращенные элементы для работы fromString по ним
    F = Forward
    R = Rear

class ESide( BaseEnum ):
    Left      = auto()
    Right     = auto()
    Undefined = auto()
    Default   = Right

    # сокращенные элементы для работы fromString по ним
    L         = Left
    R         = Right
    U         = Undefined

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
            print( f"{SC.sError} SNodePlace can't convert from '{data}'!" )
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
            nodeID_2 = l[1]
            pos      = int( l[2] )
        except:
            print( f"{SC.sError} SEdgePlace can't convert from '{data}'!" )
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
               
               SGA.linkLeft   : SNodePlace,
               SGA.linkRight  : SNodePlace,
               SGA.linkPlace  : SNodePlace,

               SGA.chargeSide : ESide,
               SGA.chargeAddress : BT.CConnectionAddress,
               SGA.chargeStage: PST.EChargeStage,
               SGA.powerState : PST.EChargeState,

               SGA.sensorAddress : MT.CRegisterAddress
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
