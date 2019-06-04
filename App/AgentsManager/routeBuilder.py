import math
from copy import deepcopy
from collections import namedtuple

from Lib.Common.Graph_NetObjects import graphNodeCache
from Lib.Common.GraphUtils import getAgentAngle, edgesListFromNodes
from Lib.Common import StorageGraphTypes as SGT
from Lib.Common.Vectors import Vector2

RH_LOW = 0
RH_HIGH = 1

hysteresis = 30
shiftFract = 10.0
shiftLeast = 100

widthTypeToChar   = { SGT.EWidthType.Narrow: 'N', SGT.EWidthType.Wide: 'W' }
railHeightToChar  = { RH_LOW: 'L', RH_HIGH:'H' }

sensorSideToChar  = { (SGT.ESensorSide.SLeft,    SGT.EDirection.F): 'L',
                      (SGT.ESensorSide.SLeft,    SGT.EDirection.R): 'R',

                      (SGT.ESensorSide.SRight,   SGT.EDirection.F): 'R',
                      (SGT.ESensorSide.SRight,   SGT.EDirection.R): 'L',

                      (SGT.ESensorSide.SBoth,    SGT.EDirection.F): 'B',
                      (SGT.ESensorSide.SPassive, SGT.EDirection.F): 'P',

                      (SGT.ESensorSide.SBoth,    SGT.EDirection.R): 'B',
                      (SGT.ESensorSide.SPassive, SGT.EDirection.R): 'P'
                    }

directionToChar = { SGT.EDirection.F: "F",
                    SGT.EDirection.R: "R",
                    SGT.EDirection.Error: "E"
                  }

curvatureToChar      = { SGT.ECurvature.Straight: 'S', SGT.ECurvature.Curve: 'C' }
widthTypeToLedgeSize = { SGT.EWidthType.Narrow: SGT.sensorNarr, SGT.EWidthType.Wide: SGT.sensorWide }
dirToK               = { SGT.EDirection.F : 1,
                         SGT.EDirection.R : -1,
                         SGT.EDirection.Error : 1
                       }

# SI_Item = namedtuple('SII' , 'length K edge pos')

class SI_Item:
    def __init__( self, length= None, K= None, edge= None, pos= None ):
        self.length = length
        self.K      = K
        self.edge   = edge
        self.pos    = pos

    def __repr__( self ):
        return f"< SII (length={self.length} K={self.K} edge={self.edge} pos={self.pos}) >\n"


class SRailSegment:
    def __init__(self, length, railHeight, sensorSide, widthType, curvature):
        self.length = length
        self.railHeight = railHeight
        self.sensorSide = sensorSide
        self.widthType = widthType
        self.curvature = curvature

    def __repr__(self):
        return f"length:{self.length} railHeight:{self.railHeight} sensorSide:{self.sensorSide} widthType:{self.widthType.name} curvature:{self.curvature}"

class CRouteBuilder():
    """Class to generate a list of correct commands in @WO/@DP/... notation for a given start and stop node"""
    def __init__(self):
        self.graphRootNode = graphNodeCache()

    @property
    def nxGraph(self):
        return self.graphRootNode().nxGraph
    
    def edgeSize( self, tKey ):
        return self.nxGraph.edges()[ tKey ][ SGT.s_edgeSize ]

    def LedgeSizeByEdge( self, tKey ):
        widthType = SGT.EWidthType.fromString( self.nxGraph.edges()[ tKey ][ SGT.s_widthType ] )
        ledgeSize = widthTypeToLedgeSize[ widthType ]
        return ledgeSize

    def buildRoute(self, nodeList, agent_angle):
        """Main function to call. Gnerates a list of correct commands in @WO/@DP/... notation for a given start and stop node"""
        #TODO: not uses orientation at current moment

        SegmentsInfoItems = []
        commands = []
        if len( nodeList ) < 2:
            return commands, SegmentsInfoItems

        # 0) Split path by fractures
        pathParts = self.splitPathByFractures(nodeList)

        angle = agent_angle
        for pathPart in pathParts:
            angle, direction = self.getDirection( (pathPart[0], pathPart[1]), angle )
            """
            path part is a node sequence with constans rail width and direction of movement. 
            Shuttle should start to move at the beginning of pathPart, and do full stop at the end 
            """
            # 1) generate rails from edges
            rails = self.nodeListToRails(pathPart)

            railStartCurvature = rails[0].curvature

            # 2) add ledge
            ledgeNode = self.findNodeForLedge(pathPart[-2], pathPart[-1])
            ledgeRailList = self.nodeListToRails([pathPart[-1], ledgeNode])

            # widthType = SGT.EWidthType.fromString( self.nxGraph[ pathPart[-2] ][ pathPart[-1] ] [ SGT.s_widthType ] )
            # ledgeSize = widthTypeToLedgeSize[ widthType ]
            ledgeSize = self.LedgeSizeByEdge( ( pathPart[-2], pathPart[-1] ) )

            ledge = self.takeRailListPart( ledgeRailList, ledgeSize )
            railsWithLedge = rails + ledge

            sourceRailList =  self.glueSameRailListParts(railsWithLedge)
            SegmentsInfoItems = SegmentsInfoItems + [ SI_Item( length = railSegment.length, K = dirToK[ direction ], edge="", pos=0 ) for railSegment in sourceRailList ]

            # 3) truncate the path by agen's width or length, depending on the current width, (because agents move by sensors)
            railListWithLedgeCuttedFromBegin = self.cutRailListFromBegin(railsWithLedge, ledgeSize)

            # 4) shift the path by hysteresis
            railListWithHystShift = self.shiftRailListByHyst( railListWithLedgeCuttedFromBegin )
            # railListWithHystShift = railListWithLedgeCuttedFromBegin

            # 5) adjust the curvature at the beggining of the path
            railListWithAdjustedCurvature = railListWithHystShift
            if railStartCurvature == SGT.ECurvature.Curve.name:
                railListWithAdjustedCurvature = self.setCurvatureFromBegin(railListWithHystShift, ledgeSize, railStartCurvature)

            # 6) merge all the rails with the same shape
            gluedRailList = self.glueSameRailListParts(railListWithAdjustedCurvature)

            # 7) Add delta to rails when rail type change exists at the end of a segment
            railListWithAddedDelta = self.addDeltaToRailList( gluedRailList )

            commands.append( self.gluedRailListToCommands(railListWithAddedDelta, direction))

            # Доворачивание угла проходом по всем граням сиквенса, для корректного определения направления на след. итерации расчета
            for i in range( len(pathPart) -1  ):
                angle, direction = self.getDirection( (pathPart[i], pathPart[i+1]), angle )

        # выявление позиций для DE
        edgesList = edgesListFromNodes( nodeList )
        edgesList.append( (nodeList[-1], ledgeNode) )
        startEdgeIdx = 0
        # l = self.LedgeSizeByEdge( edgesList[0] ) - hysteresis # стартовое смещение т.к. челнок пузом стоит на стартовой ноде
        l = 0
        for SII in SegmentsInfoItems:
            l = l + SII.length
            for i in range( startEdgeIdx, len(edgesList) ):
                tKey = edgesList[ i ]
                edgeSize = self.edgeSize( tKey )
                if edgeSize < l:
                    l -= edgeSize
                    continue
                startEdgeIdx = i
                SII.edge = tKey
                SII.pos = l
                break

        # print( SegmentsInfoItems, edgesList )

        return commands, SegmentsInfoItems

    def getDirection(self, tEdgeKey, agent_angle):
        DirDict = { True: SGT.EDirection.R, False: SGT.EDirection.F, None: SGT.EDirection.Error }
        rAngle, bReverse = getAgentAngle(self.nxGraph, tEdgeKey, agent_angle)
        return math.degrees(rAngle), DirDict[bReverse]

    def splitPathByFractures(self, path):
        fracturedPath = []
        fracturedPathSegment = []
        nodes_count = len(path)
        if nodes_count > 2:
            fracturedPathSegment.append(path[0])
            for i in range(1, nodes_count - 1):
                np = path[i-1]
                nc = path[i]
                nn = path[i+1]

                xp = self.nxGraph.nodes[np][SGT.s_x]
                yp = self.nxGraph.nodes[np][SGT.s_y]
                xc = self.nxGraph.nodes[nc][SGT.s_x]
                yc = self.nxGraph.nodes[nc][SGT.s_y]
                xn = self.nxGraph.nodes[nn][SGT.s_x]
                yn = self.nxGraph.nodes[nn][SGT.s_y]

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

        xp = self.nxGraph.nodes[lastNode][SGT.s_x]
        yp = self.nxGraph.nodes[lastNode][SGT.s_y]
        xc = self.nxGraph.nodes[  node  ][SGT.s_x]
        yc = self.nxGraph.nodes[  node  ][SGT.s_y]

        vec0 = Vector2(xc - xp, yc - yp)
        vec0 = vec0.unit()

        bestNode = False
        bestAngle = 360.0

        for edge in out_edges:
            xn = self.nxGraph.nodes[ edge[1] ][SGT.s_x]
            yn = self.nxGraph.nodes[ edge[1] ][SGT.s_y]
            vec1 = Vector2(xn - xc, yn - yc)
            vec1 = vec1.unit()

            angle = math.degrees( vec0.angle(vec1) )
            if angle < bestAngle:
                bestAngle = angle
                bestNode = edge[1]
        
        return bestNode

    def takeRailListPart(self, railList, length):
        # function takes railList and return only part of it with specified length
        outRailList = []
        for rail in railList:
            if rail.length < length:
                outRailList.append(rail)
                length = length - rail.length
            else:
                cuttedRailSegment = deepcopy( rail )
                cuttedRailSegment.length = length
                outRailList.append( cuttedRailSegment )
                return outRailList
        return outRailList

    def cutRailListFromBegin(self, railList, length):
        # function takes railList and cuts a part of it with specified length from the beginning
        outRailList = []
        self.length = length
        for rail in railList:
            if rail.length < self.length:
                #drop this rail
                self.length = self.length - rail.length
            else:
                if self.length > 0:
                    cuttedRailSegment = deepcopy(rail)
                    cuttedRailSegment.length = rail.length - self.length
                    outRailList.append(cuttedRailSegment)
                    self.length = 0
                else:
                    outRailList.append(rail)

        return outRailList

    def setCurvatureFromBegin(self, railList, length, curvature):
        lengthSetted = 0
        for rail in railList:
            rail.curvature = curvature
            lengthSetted += rail.length
            if lengthSetted >= length:
                return railList


    def nodeListToRails(self, path):
        rails = []
        if len(path) >= 1:
            for i in range(0, len(path) - 1):
                n0 = path[i]
                n1 = path[i + 1]
                edge = self.nxGraph[n0][n1]
                highRailSizeFrom = edge[ SGT.s_highRailSizeFrom ]
                highRailSizeTo   = edge[ SGT.s_highRailSizeTo   ]
                edgeSize         = edge[ SGT.s_edgeSize         ]
                sensorSide       = SGT.ESensorSide.fromString( edge[ SGT.s_sensorSide ] )
                widthType        = SGT.EWidthType.fromString ( edge[ SGT.s_widthType  ] )
                curvature        = SGT.ECurvature.fromString ( edge[ SGT.s_curvature  ] )

                if highRailSizeFrom > 0:
                    railSegment = SRailSegment(highRailSizeFrom, RH_HIGH, sensorSide, widthType, curvature)                    
                    rails.append(railSegment)

                rail_seg_length = edgeSize - highRailSizeFrom - highRailSizeTo
                if rail_seg_length > 0 :
                    railSegment = SRailSegment(rail_seg_length, RH_LOW, sensorSide, widthType, curvature)
                    rails.append(railSegment)

                if highRailSizeTo > 0:
                    railSegment = SRailSegment(highRailSizeTo, RH_HIGH, sensorSide, widthType, curvature)
                    rails.append(railSegment)
        return rails

    def glueSameRailListParts(self, railList):
        outRailList = []
        length     = railList[0].length
        railHeight = railList[0].railHeight
        sensorSide = railList[0].sensorSide
        widthType  = railList[0].widthType
        curvature  = railList[0].curvature

        for rail in railList[1:]:
            if (rail.railHeight == railHeight) and (rail.sensorSide == sensorSide) and (rail.curvature == curvature):
                length = length + rail.length
            else:
                newRail = SRailSegment(length, railHeight, sensorSide, widthType, curvature)
                outRailList.append(newRail)

                length     = rail.length
                railHeight = rail.railHeight
                sensorSide = rail.sensorSide
                widthType  = rail.widthType
                curvature  = rail.curvature

        newRail = SRailSegment(length, railHeight, sensorSide, widthType, curvature)
        outRailList.append(newRail)
        return outRailList

    def shiftRailListByHyst(self, railList):
        # encrease first segment by hyst, decrease last segment by hyst
        railList[0].length  = railList[0].length + hysteresis
        railList[-1].length = railList[-1].length - hysteresis

        # если длина рельса была меньше, чем величина гистерезиса, компенсируем отрицательное значение предыдущими рельсами 
        while railList[-1].length < 0:
            d = railList[-1].length
            del railList[-1]
            railList[-1].length += d

        return railList

    def shiftBack( self, edgesList, tKey, pos, delta ):
        startEdgdeIDX = edgesList.index(tKey)

        for edgeIDX in range( startEdgdeIDX, 0-1, -1 ):
            if pos >= delta:
                pos = pos - delta
                break
            else:
                delta = delta - pos
                if edgeIDX >= 1:
                    pos = self.edgeSize( edgesList[ edgeIDX - 1 ] )
                else:
                    pos = 0
                    break

        return edgesList[ edgeIDX ], pos


    # def shiftPos(self, edgesList, tKey, pos, delta):
    #     edgdeIDX = edgesList.index(tKey)
    #     step = 1 if delta > 0 else -1

    #     while (delta*step) > 0:
    #         edgeSize = self.nxGraph.edges()[ edgesList[edgdeIDX] ][ SGT.s_edgeSize ]


    #         if new_delta != 0:
    #             delta = new_delta
    #             edgdeIDX += step
    #             pos = self.nxGraph.edges()[ edgesList[edgdeIDX] ][ SGT.s_edgeSize ] if step < 0 else 0
    #             print(pos, delta)
    #         else:
    #             pos = pos + delta

    #     return edgesList[edgdeIDX], pos

    
    def addDeltaToRailList(self, railList):
        # adding delta to rail size to take into account possible wheels slippage, etc.
        # delta only should be added for rail segment with rail height change at the end
        for i in range(0, len(railList)-1 ):
            rail = railList[i]
            railNext = railList[i+1]

            if rail.railHeight != railNext.railHeight:
                length = rail.length
                delta = length * (shiftFract/100.0)
                delta = shiftLeast if delta < shiftLeast else delta
                length = length + delta
                rail.length = length
        
        return railList

    def gluedRailListToCommands(self, railList, temp__direction):
        commands = []
        widthTypeChar = widthTypeToChar[ railList[0].widthType ]
        direction = temp__direction
        commands.append('@SB')
        commands.append( f"@WO:{widthTypeChar}" )

        for rail in railList:
            lengthStr = ('{:06d}').format(int(rail.length))
            railHeightStr = railHeightToChar[rail.railHeight]
            sensorSideStr = sensorSideToChar[ (rail.sensorSide, direction) ]
            curvatureChar = curvatureToChar[ rail.curvature ]
            directionChar = directionToChar[ direction ]
            command = f"@DP:{lengthStr},{ directionChar },{railHeightStr},{sensorSideStr},{curvatureChar}"
            commands.append( command )
        
        commands.append('@SE')
        return commands











