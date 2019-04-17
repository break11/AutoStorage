import unittest
import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )
from Lib.Common.Graph_NetObjects import loadGraphML_to_NetObj, graphNodeCache
from Lib.Net.NetObj_Manager import CNetObj_Manager
from App.AgentsManager.routeBuilder import CRouteBuilder

CNetObj_Manager.initRoot()
loadGraphML_to_NetObj( sFName = "./UnitTests/magadanskaya.graphml", bReload = False)

class CRouteCase():
    def __init__(self):
        self.startNode   = ""
        self.endNode     = ""
        self.agentAngle  = 0
        self.sCommands = ""

    def __str__(self):
        return f"{self.__class__.__name__}: {str( vars(self) )}"


routeCases:list = []

with open("./UnitTests/routeCases.txt", 'r') as routes_file:
    for line in routes_file:

        route = line.split("|")
        input_data = route[0].split(" ")

        case = CRouteCase()
        case.startNode   = input_data[0]
        case.endNode     = input_data[1]
        case.agentAngle  = float( input_data[2] )
        case.sCommands = route[1][:-1]

        routeCases.append( case )

routeBuilder = CRouteBuilder()

# RouteCase 8 36 180.0
testCommandList_8_36_180_Answer = [
[
"@SB",
"@WO:N",
"@DP:000408,F,H,B,S",
"@DP:000700,F,L,B,S",
"@DP:004730,F,H,L,S",
"@DP:002590,F,L,L,C",
"@DP:000350,F,L,B,C",
"@DP:000350,F,L,R,S",
"@DP:002600,F,L,L,C",
"@DP:000650,F,L,B,S",
"@DP:000640,F,H,B,S",
"@DP:002442,F,L,B,S",
"@DP:000505,F,H,P,S",
"@DP:000714,F,L,P,S",
"@DP:000005,F,H,P,S",
"@SE",
],
[
"@SB",
"@WO:W",
"@DP:000490,F,H,P,S",
"@DP:000675,F,L,L,S",
"@DP:000374,F,H,L,S",
"@DP:000751,F,L,L,S",
"@DP:000374,F,H,L,S",
"@DP:000033,F,L,L,S",
"@SE"
]
]

class TestRouteBuilder(unittest.TestCase):

    def test_buildRoute(self):
        self.maxDiff = 3000
        
        i = 1
        correctCases = []
        for case in routeCases:
            # print( i, "  ", case )

            route = routeBuilder.buildRoute( nodeFrom = case.startNode, nodeTo = case.endNode, agent_angle = case.agentAngle )

            CommandsList = []
            for l in route:
                for command in l:
                    CommandsList.append( command )

            route_str = ",".join( CommandsList )

            correct = route_str == case.sCommands
            print  (i,  correct  )
            if correct: correctCases.append(i)

            i+=1
            # self.assertEqual  (  "route = routeBuilder.buildRoute", "route = routeBuilder.buildRout1"  )
        print( len( correctCases ), "   ", correctCases )

if __name__ == '__main__':
    unittest.main()