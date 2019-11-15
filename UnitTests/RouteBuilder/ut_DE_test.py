#!/usr/bin/python3.7

import unittest
import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )

from Lib.Common.Graph_NetObjects import loadGraphML_to_NetObj, graphNodeCache
from Lib.Net.NetObj_Manager import CNetObj_Manager
from App.AgentsManager.routeBuilder import CRouteBuilder, edgesListFromNodes, SI_Item, ERouteStatus

sDir = "./UnitTests/RouteBuilder/"

CNetObj_Manager.initRoot()
loadGraphML_to_NetObj( sFName = sDir + "DE_test.graphml", bReload = False)
graphRootNode = graphNodeCache()

routeBuilder = CRouteBuilder()

narrowNodesList = ["a", "b", "c", "d", "e", "f", "g", "i"]

wideNodesList_1 = ["q", "s", "k", "l", "m", "n"]
wideNodesList_2 = ["k", "l", "m"]

mixNodesList_1  = ["j", "k", "l"]
mixNodesList_2  = ["i", "j", "k", "s", "q"]
mixNodesList_3  = ["q", "s", "k", "j", "i", "g", "f", "e", "d", "c", "b", "a"]

class CTestDE(unittest.TestCase):
    def test_DE( self ):
        ###############################################################################################

        SII_Narrow = [ SI_Item (length=488, K=1, edge=('b', 'c'), pos=158),
                       SI_Item (length=100, K=1, edge=('b', 'c'), pos=258),
                       SI_Item (length=300, K=1, edge=('c', 'd'), pos=258),
                       SI_Item (length=150, K=1, edge=('d', 'e'), pos=108),
                       SI_Item (length=250, K=1, edge=('e', 'f'), pos=58),
                       SI_Item (length=100, K=1, edge=('e', 'f'), pos=158),
                       SI_Item (length=400, K=1, edge=('f', 'g'), pos=258),
                       SI_Item (length=342, K=1, edge=('g', 'i'), pos=300),
                     ]

        route, SII_Narrow_test, routeStatus = routeBuilder.buildRoute( nodeList = narrowNodesList, agent_angle = 0 )
        self.assertEqual( SII_Narrow, SII_Narrow_test )
        self.assertEqual( routeStatus, ERouteStatus.Normal )

        ###############################################################################################

        SII_Wide_1 = [ SI_Item (length=430, K=-1, edge=('q', 's'), pos=400),
                     SI_Item (length=380, K=-1, edge=('s', 'k'), pos=180),
                     SI_Item (length=360, K=-1, edge=('s', 'k'), pos=540),
                     SI_Item (length=380, K=-1, edge=('k', 'l'), pos=360),
                     SI_Item (length=900, K=-1, edge=('m', 'n'), pos=100),
                     SI_Item (length=300, K=-1, edge=('m', 'n'), pos=400),
                     SI_Item (length=200, K=-1, edge=('m', 'n'), pos=600),
                    ]

        route, SII_Wide_1_test, routeStatus = routeBuilder.buildRoute( nodeList = wideNodesList_1, agent_angle = 0 )
        self.assertEqual( SII_Wide_1, SII_Wide_1_test )
        self.assertEqual( routeStatus, ERouteStatus.Normal )

        ###############################################################################################

        SII_Wide_2 = [ SI_Item (length=390, K=-1, edge=('k', 'l'), pos=360),
                       SI_Item (length=800, K=-1, edge=('l', 'm'), pos=600),
                     ]


        route, SII_Wide2_test, routeStatus = routeBuilder.buildRoute( nodeList = wideNodesList_2, agent_angle = 0 )
        self.assertEqual( SII_Wide_2, SII_Wide2_test )
        self.assertEqual( routeStatus, ERouteStatus.Normal )

        ##############################################################################################

        SII_Mix_1 = [ SI_Item(length=93,  K=1,  edge=('j', 'k'), pos=63),
                      SI_Item(length=614, K=1,  edge=('j', 'k'), pos=677),
                      SI_Item(length=35,  K=1,  edge=('j', 'k'), pos=712),
                      SI_Item(length=390, K=-1, edge=('k', 'l'), pos=360),
                      SI_Item(length=200, K=-1, edge=('k', 'l'), pos=560),
                    ]

        route, SII_Mix1_test, routeStatus = routeBuilder.buildRoute( nodeList = mixNodesList_1, agent_angle = 0 )
        self.assertEqual( SII_Mix_1, SII_Mix1_test )
        self.assertEqual( routeStatus, ERouteStatus.Normal )

        #############################################################################################

        SII_Mix_2 = [ SI_Item (length=288, K=1, edge=('i', 'j'), pos=258),
                      SI_Item (length=405, K=1, edge=('j', 'k'), pos=63),
                      SI_Item (length=614, K=1, edge=('j', 'k'), pos=677),
                      SI_Item (length=35,  K=1, edge=('j', 'k'), pos=712),
                      SI_Item (length=390, K=1, edge=('k', 's'), pos=360),
                      SI_Item (length=800, K=1, edge=('s', 'q'), pos=600),
                    ]

        route, SII_Mix2_test, routeStatus = routeBuilder.buildRoute( nodeList = mixNodesList_2, agent_angle = 0 )
        self.assertEqual( SII_Mix_2, SII_Mix2_test )
        self.assertEqual( routeStatus, ERouteStatus.Normal )

        #############################################################################################

        SII_Mix_3 = [ SI_Item (length=430, K=1, edge=('q', 's'), pos=400),
                      SI_Item (length=380, K=1, edge=('s', 'k'), pos=180),
                      SI_Item (length=380, K=1, edge=('s', 'k'), pos=560),
                      SI_Item (length=400, K=1, edge=('k', 'j'), pos=370),
                      SI_Item (length=600, K=1, edge=('j', 'i'), pos=258),
                      SI_Item (length=400, K=1, edge=('i', 'g'), pos=58),
                      SI_Item (length=100, K=1, edge=('i', 'g'), pos=158),
                      SI_Item (length=250, K=1, edge=('g', 'f'), pos=108),
                      SI_Item (length=150, K=1, edge=('g', 'f'), pos=258),
                      SI_Item (length=300, K=1, edge=('f', 'e'), pos=258),
                      SI_Item (length=100, K=1, edge=('e', 'd'), pos=58),
                      SI_Item (length=800, K=1, edge=('c', 'b'), pos=258),
                      SI_Item (length=342, K=1, edge=('b', 'a'), pos=300),
                    ]

        route, SII_Mix3_test, routeStatus = routeBuilder.buildRoute( nodeList = mixNodesList_3, agent_angle = 180 )
        self.assertEqual( SII_Mix_3, SII_Mix3_test )
        self.assertEqual( routeStatus, ERouteStatus.Normal )

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
