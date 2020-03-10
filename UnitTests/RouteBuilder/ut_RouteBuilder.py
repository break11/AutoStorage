#!/usr/bin/python3.7

import unittest
import sys
import os

from networkx import shortest_path

sys.path.append( os.path.abspath(os.curdir)  )

from Lib.GraphEntity.Graph_NetObjects import loadGraphML_to_NetObj, graphNodeCache
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.AgentEntity.routeBuilder import CRouteBuilder, ERouteStatus
import Lib.GraphEntity.Graph_NetObjects as GNO
import Lib.Common.GraphUtils as gu
from Lib.AgentEntity.AgentDataTypes import MS


sDir = "./UnitTests/RouteBuilder/"

CNetObj_Manager.initRoot()
CNetObj_Manager.rootObj.queryObj( GNO.s_Graph, GNO.CGraphRoot_NO ) # type:ignore
loadGraphML_to_NetObj( sFName = sDir + "magadanskaya.graphml" )

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

            shortestPath = shortest_path( graphNodeCache().nxGraph, case.startNode, case.endNode )

            route, SII, routeStatus = routeBuilder.buildRoute( nodeList = shortestPath, agent_angle = case.agentAngle )

            CommandsList = []
            for sequence in route:
                for command in sequence:
                    if command.data is None:
                        data = ""
                    else:
                        data = command.data.toString( bShortForm=True )

                    CommandsList.append( f"{command.event.toStr()}{MS}{data}" )

            route_str = ",".join( CommandsList )

            self.assertEqual( route_str, case.sCommands )
            self.assertEqual( routeStatus, ERouteStatus.Normal )        

            # rString = { True : "OK", False : "FAILED" }
            # status = route_str == case.sCommands
            # if status:
            #     n += 1
                # f.write( case.toString() )
            # print( f"RouteCase {case.UID}: {case.startNode} {case.endNode} {case.agentAngle} \t{rString[status]}" )
        # f.close()
        # print( "Passed cases", n )


if __name__ == "__main__":
    unittest.main()