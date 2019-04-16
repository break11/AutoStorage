import unittest
import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )
from Lib.Common.Graph_NetObjects import loadGraphML_to_NetObj, graphNodeCache
from Lib.Net.NetObj_Manager import CNetObj_Manager
from App.AgentsManager.routeBuilder import CRouteBuilder

CNetObj_Manager.initRoot()
loadGraphML_to_NetObj( sFName = "./GraphML/magadanskaya.graphml", bReload = False)
# graphRootNode = graphNodeCache()

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
        route = routeBuilder.buildRoute( nodeFrom = "8", nodeTo = "36", temp__directionStr = "F")
        self.assertEqual  (  route, testCommandList_8_36_180_Answer  )

if __name__ == '__main__':
    unittest.main()