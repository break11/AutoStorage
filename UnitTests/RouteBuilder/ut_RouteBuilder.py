#!/usr/bin/python3.7

import unittest
import sys
import os

from networkx import shortest_path

sys.path.append( os.path.abspath(os.curdir)  )
from Lib.Common.Graph_NetObjects import loadGraphML_to_NetObj, graphNodeCache
from Lib.Net.NetObj_Manager import CNetObj_Manager
from App.AgentsManager.routeBuilder import CRouteBuilder

sDir = "./UnitTests/RouteBuilder/"

CNetObj_Manager.initRoot()
loadGraphML_to_NetObj( sFName = sDir + "magadanskaya.graphml", bReload = False)
graphRootNode = graphNodeCache()

class CRouteCase():
    genUID = 0
    def __init__(self):
        CRouteCase.genUID+=1
        self.UID = CRouteCase.genUID
        self.startNode   = ""
        self.endNode     = ""
        self.agentAngle  = 0
        self.sCommands = ""

    def __str__(self):
        return f"{self.__class__.__name__}: {str( vars(self) )}"


routeCases:list = []

with open( sDir + "routeCases.txt" , 'r') as routes_file:
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

class TestRouteBuilder(unittest.TestCase):

    def test_buildRoute(self):
        self.maxDiff = 3000

        for case in routeCases:

            shortestPath = shortest_path( graphRootNode().nxGraph, case.startNode, case.endNode )

            route, SLL = routeBuilder.buildRoute( nodeList = shortestPath, agent_angle = case.agentAngle )

            CommandsList = []
            for sequence in route:
                for command in sequence:
                    CommandsList.append( command )

            route_str = ",".join( CommandsList )

            self.assertEqual( route_str, case.sCommands )
            # status = "OK" if (route_str == case.sCommands) else "FAILED"
            # print( f"RouteCase {case.UID}: {case.startNode} {case.endNode} {case.agentAngle} \t{status}" )

if __name__ == '__main__':
    unittest.main()
