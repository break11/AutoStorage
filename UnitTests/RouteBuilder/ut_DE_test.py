#!/usr/bin/python3.7

import unittest
import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )
from Lib.Common.Graph_NetObjects import loadGraphML_to_NetObj, graphNodeCache
from Lib.Net.NetObj_Manager import CNetObj_Manager
from App.AgentsManager.routeBuilder import CRouteBuilder, edgesListFromNodes, SI_Item

sDir = "./UnitTests/RouteBuilder/"

CNetObj_Manager.initRoot()
loadGraphML_to_NetObj( sFName = sDir + "DE_test.graphml", bReload = False)
graphRootNode = graphNodeCache()

routeBuilder = CRouteBuilder()
narrowNodesList = [ "a", "b", "c", "d", "e", "f", "g", "i" ]
wideNodesList   = [ "q", "s", "k", "l", "m", "n"]

class CTestDE(unittest.TestCase):
    def test_DE( self ):
        SII_Narrow = [ SI_Item (length=800, K=1, edge=('b', 'c'), pos=158),
                       SI_Item (length=100, K=1, edge=('b', 'c'), pos=258),
                       SI_Item (length=300, K=1, edge=('c', 'd'), pos=258),
                       SI_Item (length=150, K=1, edge=('d', 'e'), pos=108),
                       SI_Item (length=250, K=1, edge=('e', 'f'), pos=58),
                       SI_Item (length=100, K=1, edge=('e', 'f'), pos=158),
                       SI_Item (length=400, K=1, edge=('f', 'g'), pos=258),
                       SI_Item (length=342, K=1, edge=('g', 'i'), pos=300),
                     ]

        route, SII_Narrow_test = routeBuilder.buildRoute( nodeList = narrowNodesList, agent_angle = 0 )
        self.assertEqual( SII_Narrow[0], SII_Narrow_test[0] )

        # print( route )
        # print( SII )


    def test_shiftPos(self):
        narrowEdgesList = edgesListFromNodes(narrowNodesList)

        self.assertEqual( routeBuilder.shiftPos(edgesList=narrowEdgesList, tKey= ("c","d"), pos = 200, delta = -100),    ( ('c','d'), 100) )
        self.assertEqual( routeBuilder.shiftPos(edgesList=narrowEdgesList, tKey= ("c","d"), pos = 200, delta = -200),    ( ('b','c'), 300) )
        self.assertEqual( routeBuilder.shiftPos(edgesList=narrowEdgesList, tKey= ("c","d"), pos = 200, delta = -500),    ( ('a','b'), 300) )
        self.assertEqual( routeBuilder.shiftPos(edgesList=narrowEdgesList, tKey= ("c","d"), pos = 200, delta = -700),    ( ('a','b'), 100) )
        self.assertEqual( routeBuilder.shiftPos(edgesList=narrowEdgesList, tKey= ("c","d"), pos = 200, delta = -2000),   ( ('a','b'), 0  ) )

        self.assertEqual( routeBuilder.shiftPos(edgesList=narrowEdgesList, tKey= ("c","d"), pos = 200, delta = 100),     ( ('c','d'), 300) )
        self.assertEqual( routeBuilder.shiftPos(edgesList=narrowEdgesList, tKey= ("c","d"), pos = 200, delta = 200),     ( ('d','e'), 100) )
        self.assertEqual( routeBuilder.shiftPos(edgesList=narrowEdgesList, tKey= ("c","d"), pos = 200, delta = 500),     ( ('e','f'), 100) )
        self.assertEqual( routeBuilder.shiftPos(edgesList=narrowEdgesList, tKey= ("c","d"), pos = 200, delta = 700),     ( ('e','f'), 300) )
        self.assertEqual( routeBuilder.shiftPos(edgesList=narrowEdgesList, tKey= ("c","d"), pos = 200, delta = 2000),    ( ('g','i'), 300) )



if __name__ == '__main__':
    unittest.main()
