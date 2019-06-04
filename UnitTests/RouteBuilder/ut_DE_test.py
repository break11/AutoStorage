#!/usr/bin/python3.7

import unittest
import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )
from Lib.Common.Graph_NetObjects import loadGraphML_to_NetObj, graphNodeCache
from Lib.Net.NetObj_Manager import CNetObj_Manager
from App.AgentsManager.routeBuilder import CRouteBuilder, edgesListFromNodes

sDir = "./UnitTests/RouteBuilder/"

CNetObj_Manager.initRoot()
loadGraphML_to_NetObj( sFName = sDir + "DE_test.graphml", bReload = False)
graphRootNode = graphNodeCache()

routeBuilder = CRouteBuilder()
nodesList = [ "a", "b", "c", "d", "e", "f", "g", "i" ]

class CTestDE(unittest.TestCase):
    def test_DE( self ):
        route, SII = routeBuilder.buildRoute( nodeList = nodesList, agent_angle = 0 )
        print( route )
        print( SII )

    def test_shiftPos(self):
        edgesList = edgesListFromNodes(nodesList)

        print( routeBuilder.shiftBack(edgesList=edgesList, tKey= ("c", "d"), pos = 200, delta = 801) )


if __name__ == '__main__':
    unittest.main()
