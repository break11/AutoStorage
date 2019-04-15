from networkx import shortest_path
from panda3d.core import LPoint3, LVector3
from copy import deepcopy
#from graph2panda import nodeToLPoint3

RH_LOW = 0
RH_HIGH = 1

sensorNarr = 342  # half of distance between sensors (x axis)
sensorWide = 200  # half of distance between sensors (y axis)
hysteresis = 30
shiftFract = 10
shiftLeast = 100

widthTypeToCommand  = {'Narrow':'N', 'Wide':'W'}
railHeightToCommand = {RH_LOW:'L', RH_HIGH:'H'}
sensorSideToCommand = {'SLeft':'L', 'SRight':'R', 'SBoth':'B', 'SPassive':'P'}
curvatureToCommand  = {'Straight':'S', 'Curve':'C'}
widthTypeToLedgeSize = {'Narrow':sensorNarr, 'Wide':sensorWide}

class RailSegment:
    def __init__(self, length, railHeight, sensorSide, widthType, curvature):
        self.length = length
        self.railHeight = railHeight
        self.sensorSide = sensorSide
        self.widthType = widthType
        self.curvature = curvature

    def __repr__(self):
        return str({'length':self.length, 'railHeight':self.railHeight, 'sensorSide':self.sensorSide, 'widthType':self.widthType, 'curvature':self.curvature})

class RailSegmentWithCoords:
    #def __init__(self, length, railHeight, sensorSide, widthType, curvature, posStart, posEnd):
    def __init__(self, length, railHeight, sensorSide, widthType, curvature):
        self.length = length
        self.railHeight = railHeight
        self.sensorSide = sensorSide
        self.widthType = widthType
        self.curvature = curvature
        #self.posStart = posStart
        #self.posEnd = posEnd

    def __repr__(self):
        #return str({'length':self.length, 'railHeight':self.railHeight, 'sensorSide':self.sensorSide, 'widthType':self.widthType, 'curvature':self.curvature, 'posStart':self.posStart, 'posEnd':self.posEnd})
        return str({'length': self.length, 'railHeight': self.railHeight, 'sensorSide': self.sensorSide,
                    'widthType': self.widthType, 'curvature': self.curvature})

"""
(RouteCase 8 36 180.0,"[
@SB,
@WO:N,
@DP:000408,F,H,B,S,
@DP:000700,F,L,B,S,
@DP:004730,F,H,L,S,
@DP:002590,F,L,L,C,
@DP:000350,F,L,B,C,
@DP:000350,F,L,R,S,
@DP:002600,F,L,L,C,
@DP:000650,F,L,B,S,
@DP:000640,F,H,B,S,
@DP:002442,F,L,B,S,
@DP:000505,F,H,P,S,
@DP:000714,F,L,P,S,
@DP:000005,F,H,P,S,
@SE,

@SB,
@WO:W,
@DP:000490,F,H,P,S,
@DP:000675,F,L,L,S,
@DP:000374,F,H,L,S,
@DP:000751,F,L,L,S,
@DP:000374,F,H,L,S,
@DP:000033,F,L,L,S,
@SE]")
"""

class RouteBuilder():
    """Class to generate a list of correct commands in @WO/@DP/... notation for a given start and stop node"""
    def __init__(self, nxgraph):
        self.nxgraph = nxgraph

    def buildRoute(self, nodeFrom, nodeTo, temp__directionStr):
        """Main function to call. Gnerates a list of correct commands in @WO/@DP/... notation for a given start and stop node"""
        #TODO: not uses orientation at current moment

        shortestPath = shortest_path(self.nxgraph, nodeFrom, nodeTo)
        print (shortestPath)

        # 0) Split path by fractures
        pathParts = self.splitPathByFractures(shortestPath)

        for pathPart in pathParts:
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

            width = self.nxgraph[pathPart[-2]][pathPart[-1]]['widthType']
            ledgeSize = widthTypeToLedgeSize[width]

            ledge = self.takeRailListPart(ledgeRailList, ledgeSize)
            railsWithLedge = rails + ledge

            # 3) truncate the path by agen's width or length, depending on the current width, (because agents move by sensors)
            railListWithLedgeCuttedFromBegin = self.cutRailListFromBegin(railsWithLedge, ledgeSize)

            # 4) shift the path by hysteresis
            railListWithHystShift = self.shiftRailListByHyst(railListWithLedgeCuttedFromBegin)

            # 5) adjust the curvature at the beggining of the path
            railListWithAdjustedCurvature = railListWithHystShift
            if railStartCurvature == 'Curve':
                railListWithAdjustedCurvature = self.setCurvatureFromBegin(railListWithHystShift, ledgeSize, railStartCurvature)

            # 6) merge all the rails with the same shape
            gluedRailList = self.glueSameRailListParts(railListWithAdjustedCurvature)

            # 7) Add delta to rails when rail type change exists at the end of a segment
            railListWithAddedDelta = self.addDeltaToRailList(gluedRailList)

            commands = self.gluedRailListToCommands(railListWithAddedDelta, temp__directionStr)
            print(commands)
            return commands

    def splitPathByFractures(self, path):
        #print('splitPathByFractures:')
        #print('input path = {}'.format(path))
        fracturedPath = []
        fracturedPathSegment = []
        if len(path) > 2:
            fracturedPathSegment.append(path[0])
            for i in range(1,len(path)-1):
                np = path[i-1]
                nc = path[i]
                nn = path[i+1]
                xp = self.nxgraph.nodes[np]['x']
                yp = self.nxgraph.nodes[np]['y']
                xc = self.nxgraph.nodes[nc]['x']
                yc = self.nxgraph.nodes[nc]['y']
                xn = self.nxgraph.nodes[nn]['x']
                yn = self.nxgraph.nodes[nn]['y']
                vec0 = LVector3(xc-xp, yc-yp, 0)
                vec1 = LVector3(xn-xc, yn-yc, 0)
                vec0.normalize()
                vec1.normalize()
                angle = vec0.angleDeg(vec1)
                #print([nc, angle])
                fracturedPathSegment.append(nc)
                if angle > 45.0:
                    # fracture found due to narrow->wide or direction change (ex. on curved cross)
                    fracturedPath.append(fracturedPathSegment)
                    fracturedPathSegment = [nc]
            fracturedPathSegment.append(path[-1])

            fracturedPath.append(fracturedPathSegment)

        #print('output path = {}'.format(fracturedPath))
        return fracturedPath

    def findNodeForLedge(self, lastNode, node):
        #print('findNodeForLedge')
        out_edges = self.nxgraph.out_edges(node)
        #print (out_edges)
        xp = self.nxgraph.nodes[lastNode]['x']
        yp = self.nxgraph.nodes[lastNode]['y']
        xc = self.nxgraph.nodes[node]['x']
        yc = self.nxgraph.nodes[node]['y']
        vec0 = LVector3(xc - xp, yc - yp, 0)
        vec0.normalize()
        bestNode = False
        bestAngle = 360.0
        for out_edge in out_edges:
            xn = self.nxgraph.nodes[out_edge[1]]['x']
            yn = self.nxgraph.nodes[out_edge[1]]['y']
            vec1 = LVector3(xn - xc, yn - yc, 0)
            vec1.normalize()
            angle = vec0.angleDeg(vec1)
            if angle < bestAngle:
                bestAngle = angle
                bestNode = out_edge[1]
        return bestNode



    def takeRailListPart(self, railList, length):
        # function takes railList and return only part of it with specified length
        outRailList = []
        for rail in railList:
            if rail.length < length:
                outRailList.append(rail)
                length = length - rail.length
            else:
                cuttedRailSegment = deepcopy(rail)
                cuttedRailSegment.length = length
                outRailList.append(cuttedRailSegment)
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
        print("setCurvatureFromBegin:")
        lengthSetted = 0
        for rail in railList:
            rail.curvature = curvature
            lengthSetted += rail.length
            print(lengthSetted)
            print(length)
            if lengthSetted >= length:
                return railList


    def nodeListToRails(self, path):
        rails = []
        if len(path) > 1:
            for i in range(0, len(path) - 1):
                n0 = path[i]
                n1 = path[i + 1]
                edge = self.nxgraph[n0][n1]
                #print(edge)
                highRailSizeFrom = int(edge['highRailSizeFrom'])
                highRailSizeTo = int(edge['highRailSizeTo'])
                edgeSize = int(edge['edgeSize'])
                sensorSide = edge['sensorSide']
                widthType = edge['widthType']
                curvature = edge['curvature']

                #p0 = nodeToLPoint3(self.nxgraph, n0)
                #p1 = nodeToLPoint3(self.nxgraph, n1)

                if highRailSizeFrom > 0:
                    railSegment = RailSegmentWithCoords(highRailSizeFrom, RH_HIGH, sensorSide, widthType, curvature)
                    rails.append(railSegment)

                railSegment = RailSegmentWithCoords(edgeSize - highRailSizeFrom - highRailSizeTo, RH_LOW, sensorSide, widthType, curvature)
                if railSegment.length > 0 :
                    rails.append(railSegment)

                if highRailSizeTo > 0:
                    railSegment = RailSegmentWithCoords(highRailSizeTo, RH_HIGH, sensorSide, widthType, curvature)
                    rails.append(railSegment)
        return rails
        #print(rails)


    def glueSameRailListParts(self, railList):
        outRailList = []
        length = railList[0].length
        railHeight = railList[0].railHeight
        sensorSide = railList[0].sensorSide
        widthType = railList[0].widthType
        curvature = railList[0].curvature

        for rail in railList[1:]:
            if (rail.railHeight == railHeight) and (rail.sensorSide == sensorSide) and (rail.curvature == curvature):
                length = length + rail.length
            else:
                newRail = RailSegment(length, railHeight, sensorSide, widthType, curvature)
                outRailList.append(newRail)

                length = rail.length
                railHeight = rail.railHeight
                sensorSide = rail.sensorSide
                widthType = rail.widthType
                curvature = rail.curvature

        newRail = RailSegment(length, railHeight, sensorSide, widthType, curvature)
        outRailList.append(newRail)
        return outRailList

    def shiftRailListByHyst(self, railList):
        # encrease first segment by hyst, decrease last segment by hyst
        railList[0].length = railList[0].length + hysteresis
        railList[-1].length = railList[-1].length - hysteresis
        return railList

    def addDeltaToRailList(self, railList):
        # adding delta to rail size to take into account possible wheels slippage, etc.
        # delta only should be added for rail segment with rail height change at the end
        for i in range(0, len(railList) - 1):
            rail = railList[i]
            railNext = railList[i+1]
            if rail.railHeight != railNext.railHeight:
                length = rail.length
                delta = length * (float(shiftFract)/100.0)
                if delta < shiftLeast:
                    delta = shiftLeast
                length = length + delta
                rail.length = length
        return railList

    def gluedRailListToCommands(self, railList, temp__directionStr):
        commands = []
        widthTypeStr = widthTypeToCommand[railList[0].widthType]
        #directionStr = 'F'
        directionStr = temp__directionStr
        commands.append('@SB')
        commands.append(('@WO:{:s}').format(widthTypeStr))
        for rail in railList:
            lengthStr = ('{:06d}').format(int(rail.length))
            railHeightStr = railHeightToCommand[rail.railHeight]
            sensorSideStr = sensorSideToCommand[rail.sensorSide]
            curvatureStr = curvatureToCommand[rail.curvature]
            command = ('@DP:{:s},{:s},{:s},{:s},{:s}').format(lengthStr, directionStr, railHeightStr, sensorSideStr, curvatureStr)
            commands.append(command)
        commands.append('@SE')
        return commands










