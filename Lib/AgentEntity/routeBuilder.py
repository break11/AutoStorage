import math
from copy import deepcopy
import networkx as nx
from enum import Enum, auto

from Lib.GraphEntity.Graph_NetObjects import graphNodeCache
from Lib.Common.GraphUtils import getAgentAngle, getFinalAgentAngle, edgesListFromNodes, edgeSize, pathsThroughCycles
from Lib.GraphEntity import StorageGraphTypes as SGT
from Lib.GraphEntity.StorageGraphTypes import SGA
from Lib.Common.Vectors import Vector2
from Lib.Common.StrConsts import SC
from Lib.AgentEntity.AgentServerPacket import CAgentServerPacket as ASP
import Lib.AgentEntity.AgentDataTypes as ADT
from Lib.AgentEntity.AgentServer_Event import EAgentServer_Event as EV

hysteresis = 30
shiftFract = 10.0
shiftLeast = 100

sensorSide_from_SideDir  = { (SGT.ESensorSide.SLeft,    SGT.EDirection.Forward): SGT.ESensorSide.SLeft,
                      (SGT.ESensorSide.SLeft,    SGT.EDirection.Rear)   : SGT.ESensorSide.SRight,

                      (SGT.ESensorSide.SRight,   SGT.EDirection.Forward): SGT.ESensorSide.SRight,
                      (SGT.ESensorSide.SRight,   SGT.EDirection.Rear)   : SGT.ESensorSide.SLeft,

                      (SGT.ESensorSide.SBoth,    SGT.EDirection.Forward): SGT.ESensorSide.SBoth,
                      (SGT.ESensorSide.SPassive, SGT.EDirection.Forward): SGT.ESensorSide.SPassive,

                      (SGT.ESensorSide.SBoth,    SGT.EDirection.Rear)   : SGT.ESensorSide.SBoth,
                      (SGT.ESensorSide.SPassive, SGT.EDirection.Rear)   : SGT.ESensorSide.SPassive
                    }

widthTypeToLedgeSize = { SGT.EWidthType.Narrow: SGT.sensorNarr, SGT.EWidthType.Wide: SGT.sensorWide }
dirToK               = { SGT.EDirection.Forward : 1,
                         SGT.EDirection.Rear    : -1,
                         SGT.EDirection.Error   : 1
                       }

class SI_Item:
    def __init__( self, length= None, K= None, edge= None, pos= None, angle= None ):
        self.length = length
        self.K      = K
        self.edge   = edge
        self.pos    = pos
        self.angle  = angle

    def __eq__(self, other):
        eq = True
        eq = eq and self.length == other.length
        eq = eq and self.K      == other.K
        eq = eq and self.edge   == other.edge
        eq = eq and self.pos    == other.pos

        return eq

    def __repr__( self ):
        return f"< SII (length={self.length} K={self.K} edge={self.edge} pos={self.pos} angle={self.angle}) >\n"


class CRailSegment:
    def __init__(self, length, railHeight, sensorSide, widthType, curvature):
        self.length = length
        self.railHeight = railHeight
        self.sensorSide = sensorSide
        self.widthType = widthType
        self.curvature = curvature

    def __repr__(self):
        return f"length:{self.length} railHeight:{self.railHeight} sensorSide:{self.sensorSide} widthType:{self.widthType.name} curvature:{self.curvature}\n"

class ERouteStatus(Enum):
    Normal      = auto()
    AngleError  = auto()

class CRouteBuilder():
    """Class to generate a list of correct commands in @WO/@DP/... notation for a given start and stop node"""
    @property
    def nxGraph(self):
        return graphNodeCache().nxGraph
    
    def edgeSize( self, tKey ):
        return edgeSize( self.nxGraph, tKey )

    def LedgeSizeByEdge( self, tKey ):
        widthType = self.nxGraph.edges()[ tKey ][ SGA.widthType ]
        ledgeSize = widthTypeToLedgeSize[ widthType ]
        return ledgeSize

    def buildRoute(self, nodeList, agent_angle):
        """Main function to call. Gnerates a list of correct commands in @WO/@DP/... notation for a given start and stop node"""
        #TODO: not uses orientation at current moment

        SegmentsInfoItems = []
        commands = []
        # if len( nodeList ) < 2:
        #     return commands, SegmentsInfoItems

        # 0) Split path by fractures
        Sequences = self.splitPathByFractures( nodeList )

        angle = agent_angle
        for single_sequence in Sequences:
            angle, direction = self.getDirection( (single_sequence[0], single_sequence[1]), angle )
            
            if direction == SGT.EDirection.Error:
                print( f"{SC.sError} invalid agent rotation. Build route failed." )
                return [], [], ERouteStatus.AngleError
            
            """
            path part is a node sequence with constans rail width and direction of movement. 
            Shuttle should start to move at the beginning of pathPart, and do full stop at the end 
            """
            # 1) generate rails from edges
            segments = self.nodeListToSegments( single_sequence )
            startSegmentCurv = segments[0].curvature

            # 2) add ledge
            ledgeSize = self.LedgeSizeByEdge( ( single_sequence[-2], single_sequence[-1] ) )
            
            w = 0
            ledgeNodes = [ single_sequence[-2], single_sequence[-1] ]
            # ledgeNode = self.findNodeForLedge(*l)
            # при поиске ledgeNodes суммарная длинна граней должна быть не менее половины челнока с соотв ориентацией (ledgeSize)
            while w < ledgeSize:
                ledgeNode = self.findNodeForLedge( ledgeNodes[-2], ledgeNodes[-1] )
                ledgeNodes.append( ledgeNode )
                w += edgeSize( self.nxGraph, ( ledgeNodes[-2], ledgeNodes[-1] ) )
            del ledgeNodes[0]

            # ledgeSegments = self.nodeListToSegments( l )
            ledgeSegments = self.nodeListToSegments( ledgeNodes )

            ledge = self.takeSegmentsFromBegin( ledgeSegments, ledgeSize )
            SegmentsWithLedge = segments + ledge

            # 3) truncate the path by agen's width or length, depending on the current width, (because agents move by sensors)
            SegmentsWithLedgeCuttedFromBegin = self.cutSegmentsFromBegin(SegmentsWithLedge, ledgeSize)
 
            # 4) shift the path by hysteresis
            SegmentsWithHystShift = self.shiftSegmentsByHyst( SegmentsWithLedgeCuttedFromBegin )

            sourceSegments =  self.mergeSameSegments(SegmentsWithHystShift)
            SegmentsInfoItems_Sequence = [ SI_Item( length = segment.length, K = dirToK[ direction ], edge=(), pos=0, angle=0 ) for segment in sourceSegments ]
           
            # 5) adjust the curvature at the beggining of the path
            SegmentsWithAdjustedCurvature = SegmentsWithHystShift

            if startSegmentCurv == SGT.ECurvature.Curve:
                SegmentsWithAdjustedCurvature = self.setCurvatureFromBegin( SegmentsWithHystShift, ledgeSize, startSegmentCurv )

            # 6) merge all the rails with the same shape
            mergedSegments = self.mergeSameSegments( SegmentsWithAdjustedCurvature )

            # 7) Add delta to rails when rail type change exists at the end of a segment
            SegmentsWithDelta = self.addDeltaToSegments( mergedSegments )
            commands.append( self.SegmentsToCommands( SegmentsWithDelta, direction ))

            # # Доворачивание угла проходом по всем граням сиквенса, для корректного определения направления на след. итерации расчета
            # for i in range( len(single_sequence) -1  ):
            #     angle, direction = self.getDirection( (single_sequence[i], single_sequence[i+1]), angle )
            #     SII[ i ].angle = angle

            angle = self.calc_DE_Pos( SegmentsInfoItems_Sequence, single_sequence, ledgeNodes, ledgeSize, angle )
            SegmentsInfoItems += SegmentsInfoItems_Sequence
        
        return commands, SegmentsInfoItems, ERouteStatus.Normal

    def calc_DE_Pos(self, SII_Sequince, single_sequence, ledgeNodes,  ledgeSize, angle):
        # выявление позиций для DE
        edgesList = edgesListFromNodes( single_sequence + ledgeNodes[1:] )
        startEdgeIdx = 0

        l = ledgeSize - hysteresis
        SII_Sequince[-1].length += hysteresis
        for SII in SII_Sequince:
            l = l + SII.length
            for i in range( startEdgeIdx, len(edgesList) ):
                tKey = edgesList[ i ]
                edgeSize = self.edgeSize( tKey )
                # Доворачивание угла проходом по всем граням сиквенса, для корректного определения направления на след. итерации расчета
                angle, direction = self.getDirection( (tKey[0], tKey[1]), angle )
                if edgeSize < l:
                    l -= edgeSize
                    continue
                SII.angle = angle # сохранение правильного довернутого угла в точке DE
                startEdgeIdx = i
                
                SII.edge, SII.pos = self.shiftPos( edgesList, tKey, l, -ledgeSize )
                break
        return angle
        

    def getDirection(self, tEdgeKey, agent_angle):
        DirDict = { True: SGT.EDirection.Rear, False: SGT.EDirection.Forward, None: SGT.EDirection.Error }
        angle, bReverse = getAgentAngle(self.nxGraph, tEdgeKey, agent_angle)
        return angle, DirDict[bReverse]

    def splitPathByFractures(self, path):
        fracturedPath = []
        fracturedPathSegment = []
        nodes_count = len(path)
        if nodes_count >= 2:
            fracturedPathSegment.append( path[0] )
            for i in range(1, nodes_count - 1):
                np = path[i-1]
                nc = path[i]
                nn = path[i+1]

                xp = self.nxGraph.nodes[np][SGA.x]
                yp = self.nxGraph.nodes[np][SGA.y]
                xc = self.nxGraph.nodes[nc][SGA.x]
                yc = self.nxGraph.nodes[nc][SGA.y]
                xn = self.nxGraph.nodes[nn][SGA.x]
                yn = self.nxGraph.nodes[nn][SGA.y]

                vec0 = Vector2(xc-xp, yc-yp)
                vec1 = Vector2(xn-xc, yn-yc)

                vec0 = vec0.unit()
                vec1 = vec1.unit()

                angle = math.degrees( vec0.angle(vec1) )
                fracturedPathSegment.append(nc)
                if angle > 45.0:
                    # fracture found due to narrow->wide or direction change (ex. on curved cross)
                    fracturedPath.append(fracturedPathSegment)
                    fracturedPathSegment = [nc]
            fracturedPathSegment.append(path[-1])

            fracturedPath.append(fracturedPathSegment)

        return fracturedPath

    def findNodeForLedge(self, lastNode, node):
        out_edges = self.nxGraph.out_edges(node)

        xp = self.nxGraph.nodes[lastNode][SGA.x]
        yp = self.nxGraph.nodes[lastNode][SGA.y]
        xc = self.nxGraph.nodes[  node  ][SGA.x]
        yc = self.nxGraph.nodes[  node  ][SGA.y]

        vec0 = Vector2(xc - xp, yc - yp)
        vec0 = vec0.unit()

        bestNode = False
        bestAngle = 360.0

        for edge in out_edges:
            xn = self.nxGraph.nodes[ edge[1] ][SGA.x]
            yn = self.nxGraph.nodes[ edge[1] ][SGA.y]
            vec1 = Vector2(xn - xc, yn - yc)
            vec1 = vec1.unit()

            angle = math.degrees( vec0.angle(vec1) )
            if angle < bestAngle:
                bestAngle = angle
                bestNode = edge[1]
        
        return bestNode

    def takeSegmentsFromBegin(self, Segments, length):
        # function takes railList and return only part of it with specified length
        outRailList = []
        for segment in Segments:
            if segment.length < length:
                outRailList.append(segment)
                length = length - segment.length
            else:
                cuttedSegment = deepcopy( segment )
                cuttedSegment.length = length
                outRailList.append( cuttedSegment )
                return outRailList
        return outRailList

    def cutSegmentsFromBegin(self, Segments, length):
        # function takes railList and cuts a part of it with specified length from the beginning
        outSegments = []
        self.length = length
        for segment in Segments:
            if segment.length < self.length:
                #drop this rail
                self.length = self.length - segment.length
            else:
                if self.length > 0:
                    cuttedSegment = deepcopy(segment)
                    cuttedSegment.length = segment.length - self.length
                    outSegments.append(cuttedSegment)
                    self.length = 0
                else:
                    outSegments.append(segment)

        return outSegments

    def setCurvatureFromBegin(self, Segments, length, curvature):
        lengthSetted = 0
        for segment in Segments:
            segment.curvature = curvature
            lengthSetted += segment.length
            if lengthSetted >= length:
                return Segments


    def nodeListToSegments(self, path):
        Segments = []
        if len(path) >= 1:
            for i in range(0, len(path) - 1):
                n0 = path[i]
                n1 = path[i + 1]
                edge = self.nxGraph[n0][n1]
                highRailSizeFrom = edge[ SGA.highRailSizeFrom ]
                highRailSizeTo   = edge[ SGA.highRailSizeTo   ]
                edgeSize         = edge[ SGA.edgeSize         ]
                sensorSide       = edge[ SGA.sensorSide ]
                widthType        = edge[ SGA.widthType  ]
                curvature        = edge[ SGA.curvature  ]

                if highRailSizeFrom > 0:
                    segment = CRailSegment(highRailSizeFrom, SGT.ERailHeight.High, sensorSide, widthType, curvature)                    
                    Segments.append(segment)

                seg_length = edgeSize - highRailSizeFrom - highRailSizeTo
                if seg_length > 0 :
                    segment = CRailSegment(seg_length, SGT.ERailHeight.Low, sensorSide, widthType, curvature)
                    Segments.append(segment)

                if highRailSizeTo > 0:
                    segment = CRailSegment(highRailSizeTo, SGT.ERailHeight.High, sensorSide, widthType, curvature)
                    Segments.append(segment)
        return Segments

    def mergeSameSegments(self, Segments):
        outRailList = []
        length     = Segments[0].length
        railHeight = Segments[0].railHeight
        sensorSide = Segments[0].sensorSide
        widthType  = Segments[0].widthType
        curvature  = Segments[0].curvature

        for segment in Segments[1:]:
            if (segment.railHeight == railHeight) and (segment.sensorSide == sensorSide) and (segment.curvature == curvature):
                length = length + segment.length
            else:
                newRail = CRailSegment(length, railHeight, sensorSide, widthType, curvature)
                outRailList.append(newRail)

                length     = segment.length
                railHeight = segment.railHeight
                sensorSide = segment.sensorSide
                widthType  = segment.widthType
                curvature  = segment.curvature

        newRail = CRailSegment(length, railHeight, sensorSide, widthType, curvature)
        outRailList.append(newRail)
        return outRailList

    def shiftSegmentsByHyst(self, Segments):
        # encrease first segment by hyst, decrease last segment by hyst
        Segments[0].length  = Segments[0].length + hysteresis
        Segments[-1].length = Segments[-1].length - hysteresis

        # если длина рельса была меньше, чем величина гистерезиса, компенсируем отрицательное значение предыдущими рельсами 
        while Segments[-1].length < 0:
            d = Segments[-1].length
            del Segments[-1]
            Segments[-1].length += d

        return Segments

    def shiftPos(self, edgesList, tKey, pos, delta ):
        edgeIDX = edgesList.index(tKey)
        while True:
            pos = pos + delta
            if pos <= 0:
                delta = pos
                edgeIDX -= 1

                if edgeIDX < 0: #если дельта меньше, чем расстояние до начала маршрута
                    return ( edgesList[0], 0)
                
                pos =  self.edgeSize( edgesList[edgeIDX] )
            elif pos > self.edgeSize(edgesList[edgeIDX]):

                if edgeIDX == len(edgesList) - 1: #если дельта больше, чем расстояние до конца маршрута
                    return (edgesList[edgeIDX], self.edgeSize(edgesList[edgeIDX]))
                
                delta = pos - self.edgeSize(edgesList[edgeIDX])
                edgeIDX += 1
                pos = 0
            else:
                return edgesList[edgeIDX], pos

    
    def addDeltaToSegments(self, Segments):
        # adding delta to rail size to take into account possible wheels slippage, etc.
        # delta only should be added for rail segment with rail height change at the end
        for i in range(0, len(Segments)-1 ):
            segment = Segments[i]
            nextSegment = Segments[i+1]

            if segment.railHeight != nextSegment.railHeight:
                length = segment.length
                delta = length * (shiftFract/100.0)
                delta = shiftLeast if delta < shiftLeast else delta
                length = length + delta
                segment.length = length
        
        return Segments

    def SegmentsToCommands(self, Segments, temp__direction):
        commands = []
        direction = temp__direction
        commands.append( ASP( event=EV.SequenceBegin ) )
        commands.append( ASP( event=EV.WheelOrientation, data = Segments[0].widthType ) )

        for segment in Segments:
            dpData = ADT.SDP_Data( length = int(segment.length),
                                   direction=direction,
                                   railHeight=segment.railHeight,
                                   sensorSide=sensorSide_from_SideDir[ (segment.sensorSide, direction) ],
                                   curvature=segment.curvature )
            commands.append( ASP( event=EV.DistancePassed, data=dpData ) )
        
        commands.append( ASP( event=EV.SequenceEnd ) )
        return commands