#!/usr/bin/python3.7

import unittest
import sys
import os

from networkx import shortest_path

sys.path.append( os.path.abspath(os.curdir)  )
from Lib.Common.Graph_NetObjects import loadGraphML_to_NetObj, graphNodeCache
from Lib.Net.NetObj_Manager import CNetObj_Manager
from App.AgentsManager.routeBuilder import CRouteBuilder
from Lib.Common import StorageGraphTypes as SGT
import Lib.Common.GraphUtils as gu
from Lib.AgentProtocol.AgentDataTypes import MS


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

    def toString(self):
        return f"{self.startNode} {self.endNode} {self.agentAngle}|{self.sCommands}\n"

    def __str__(self):
        return f"{self.__class__.__name__}: {str( vars(self) )}"


routeCases:list = []

with open( sDir + "routeCases_correct_700.txt" , "r") as routes_file:
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

class CTestRouteBuilder(unittest.TestCase):
    maxDiff = None

    def test_buildRoute(self):
        # n = 0
        # f = open( "./UnitTests/RouteBuilder/passed.txt", "w" )
        for case in routeCases:

            shortestPath = shortest_path( graphRootNode().nxGraph, case.startNode, case.endNode )

            route, SII = routeBuilder.buildRoute( nodeList = shortestPath, agent_angle = case.agentAngle )

            CommandsList = []
            for sequence in route:
                for command in sequence:
                    data = command.data if command.data is not None else ""
                    CommandsList.append( f"{command.event.toStr()}{MS}{data}" )

            route_str = ",".join( CommandsList )

            self.assertEqual( route_str, case.sCommands )
            rString = { True : "OK", False : "FAILED" }

            status = route_str == case.sCommands
            # if status:
            #     n += 1
                # f.write( case.toString() )
            # print( f"RouteCase {case.UID}: {case.startNode} {case.endNode} {case.agentAngle} \t{rString[status]}" )
        # f.close()
        # print( "Passed cases", n )


if __name__ == "__main__":
    unittest.main()