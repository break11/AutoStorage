import unittest

import sys
import os
import math
import networkx as nx

sys.path.append( os.path.abspath(os.curdir)  )

import Lib.Common.GraphUtils as gu
from Lib.Common.Vectors import Vector2

#доверенные значения
cos_45 = math.sqrt(2)/2
sin_45 = math.sqrt(2)/2

u_vec_0   = Vector2 (1, 0)
u_vec_45  = Vector2 (cos_45, sin_45)
u_vec_90  = Vector2 (0, 1)
u_vec_135 = Vector2 (-cos_45, sin_45)
u_vec_180 = Vector2 (-1, 0)
u_vec_225 = Vector2 (-cos_45, -sin_45)
u_vec_270 = Vector2 (0, -1)
u_vec_315 = Vector2 (cos_45, -sin_45)

deg_0   = 0.0
deg_45  = 45.0
deg_90  = 90.0
deg_135 = 135.0
deg_180 = 180.0
deg_225 = 225.0
deg_270 = 270.0
deg_315 = 315.0
deg_360 = 360.0
deg_540 = 540.0

nxGraph = nx.DiGraph()

nodeID1 = "ID1"
nodeID2 = "ID2"

nodeID3 = "ID3"
nodeID4 = "ID4"

tEdgeKey12 = (nodeID1, nodeID2)
tEdgeKey21 = (nodeID2, nodeID1)

x1, x2, y1, y2 = 10, -20, 30, -40

nxGraph.add_node(nodeID1, x=x1, y=y1)
nxGraph.add_node(nodeID2, x=x2, y=y2)
nxGraph.add_edge(nodeID1, nodeID2)
nxGraph.add_edge(nodeID2, nodeID1)

#тестируемые значения
test_u_vec_0   = Vector2(10,    0).unit()
test_u_vec_45  = Vector2(30,   30).unit()
test_u_vec_90  = Vector2(0,    99).unit()
test_u_vec_135 = Vector2(-15,  15).unit()
test_u_vec_180 = Vector2(-0.4,   0).unit()
test_u_vec_225 = Vector2(-0.1107, -0.1107).unit()
test_u_vec_270 = Vector2(0,   -1.5).unit()
test_u_vec_315 = Vector2(2506,  -2506).unit()

test_u_vec_from_0_deg   = Vector2.fromAngle( math.radians( deg_0   ) )
test_u_vec_from_45_deg  = Vector2.fromAngle( math.radians( deg_45  ) )
test_u_vec_from_90_deg  = Vector2.fromAngle( math.radians( deg_90  ) )
test_u_vec_from_135_deg = Vector2.fromAngle( math.radians( deg_135 ) )
test_u_vec_from_180_deg = Vector2.fromAngle( math.radians( deg_180 ) )
test_u_vec_from_225_deg = Vector2.fromAngle( math.radians( deg_225 ) )
test_u_vec_from_270_deg = Vector2.fromAngle( math.radians( deg_270 ) )
test_u_vec_from_315_deg = Vector2.fromAngle( math.radians( deg_315 ) )
test_u_vec_from_360_deg = Vector2.fromAngle( math.radians( deg_360 ) )
test_u_vec_from_540_deg = Vector2.fromAngle( math.radians( deg_540 ) )

test_0_rad_angle   = u_vec_0.selfAngle()
test_45_rad_angle  = u_vec_45.selfAngle()
test_90_rad_angle  = u_vec_90.selfAngle()
test_135_rad_angle = u_vec_135.selfAngle()
test_180_rad_angle = u_vec_180.selfAngle()
test_225_rad_angle = u_vec_225.selfAngle()
test_270_rad_angle = u_vec_270.selfAngle()
test_315_rad_angle = u_vec_315.selfAngle()

#############################################################

class TestMathFuncs(unittest.TestCase):


    def test_isEqual(self):
        self.assertTrue  (  u_vec_45 == u_vec_45  )
        self.assertFalse (  u_vec_45 != u_vec_45  )
        self.assertFalse (  u_vec_45 == u_vec_135 )

        self.assertTrue  (  Vector2(1.1e-9, 1) ==  Vector2(1.2e-9, 1)  )
        self.assertFalse (  Vector2(1.1e-8, 1) ==  Vector2(1.2e-8, 1)  )

    def test_unit(self):
        self.assertTrue(   test_u_vec_0    == u_vec_0     )
        self.assertTrue(   test_u_vec_45   == u_vec_45    )
        self.assertTrue(   test_u_vec_90   == u_vec_90    )
        self.assertTrue(   test_u_vec_135  == u_vec_135   )
        self.assertTrue(   test_u_vec_180  == u_vec_180   )
        self.assertTrue(   test_u_vec_225  == u_vec_225   )
        self.assertTrue(   test_u_vec_270  == u_vec_270   )
        self.assertTrue(   test_u_vec_315  == u_vec_315   )

    def test_angle(self):
        self.assertTrue(   math.isclose ( u_vec_0.angle( u_vec_0 ),   0.00 * math.pi)  )
        self.assertTrue(   math.isclose ( u_vec_0.angle( u_vec_45 ),  0.25 * math.pi)  )
        self.assertTrue(   math.isclose ( u_vec_0.angle( u_vec_90 ),  0.50 * math.pi)  )
        self.assertTrue(   math.isclose ( u_vec_0.angle( u_vec_135),  0.75 * math.pi)  )
        self.assertTrue(   math.isclose ( u_vec_0.angle( u_vec_180),  1.00 * math.pi)  )

        self.assertTrue(   math.isclose ( u_vec_0.angle( u_vec_315 ),  0.25 * math.pi)  )
        self.assertTrue(   math.isclose ( u_vec_0.angle( u_vec_270 ),  0.50 * math.pi)  )
        self.assertTrue(   math.isclose ( u_vec_0.angle( u_vec_225),   0.75 * math.pi)  )

        self.assertTrue(   math.isclose ( u_vec_45.angle( u_vec_315),  0.50 * math.pi)  )
        self.assertTrue(   math.isclose ( u_vec_180.angle( u_vec_315), 0.75 * math.pi)  )
        self.assertTrue(   math.isclose ( u_vec_135.angle( u_vec_315), 1.00 * math.pi)  )

    def test_selfAngle(self):
        self.assertTrue(   math.isclose (test_0_rad_angle,   0.00 * math.pi)  )
        self.assertTrue(   math.isclose (test_45_rad_angle,  0.25 * math.pi)  )
        self.assertTrue(   math.isclose (test_90_rad_angle,  0.50 * math.pi)  )
        self.assertTrue(   math.isclose (test_135_rad_angle, 0.75 * math.pi)  )
        self.assertTrue(   math.isclose (test_180_rad_angle, 1.00 * math.pi)  )
        self.assertTrue(   math.isclose (test_225_rad_angle, 1.25 * math.pi)  )
        self.assertTrue(   math.isclose (test_270_rad_angle, 1.50 * math.pi)  )
        self.assertTrue(   math.isclose (test_315_rad_angle, 1.75 * math.pi)  )

    def test_fromAngle(self):
        self.assertTrue(   test_u_vec_from_0_deg    == u_vec_0     )
        self.assertTrue(   test_u_vec_from_45_deg   == u_vec_45    )
        self.assertTrue(   test_u_vec_from_90_deg   == u_vec_90    )
        self.assertTrue(   test_u_vec_from_135_deg  == u_vec_135   )
        self.assertTrue(   test_u_vec_from_180_deg  == u_vec_180   )
        self.assertTrue(   test_u_vec_from_225_deg  == u_vec_225   )
        self.assertTrue(   test_u_vec_from_270_deg  == u_vec_270   )
        self.assertTrue(   test_u_vec_from_315_deg  == u_vec_315   )
        
        self.assertTrue(   test_u_vec_from_360_deg  == u_vec_0     )
        self.assertTrue(   test_u_vec_from_540_deg  == u_vec_180   )


    def test_getEdgeCoords(self):
        test_x1, test_y1, test_x2, test_y2 = gu.getEdgeCoords (nxGraph, tEdgeKey12)
        self.assertEqual( (test_x1, test_y1, test_x2, test_y2), (x1, y1, x2, y2)  )

        test_x1, test_y1, test_x2, test_y2 = gu.getEdgeCoords (nxGraph, tEdgeKey21)
        self.assertEqual( (test_x1, test_y1, test_x2, test_y2), (x2, y2, x1, y1)  )


class TestStrFuncs(unittest.TestCase):

    def test_tEdgeKeyFromStr(self):
        self.assertEqual(   gu.tEdgeKeyFromStr( f"{nodeID1},{nodeID2}" ),  tEdgeKey12   )
        self.assertEqual(   gu.tEdgeKeyFromStr( f"{nodeID1}:{nodeID2}" ),  tEdgeKey12   )
        self.assertEqual(   gu.tEdgeKeyFromStr( f"{nodeID1}-{nodeID2}" ),  tEdgeKey12   )
        self.assertEqual(   gu.tEdgeKeyFromStr( f"{nodeID1} {nodeID2}" ),  tEdgeKey12   )
        self.assertEqual(   gu.tEdgeKeyFromStr( f"{nodeID1} ,{nodeID2}" ), tEdgeKey12   )
        self.assertEqual(   gu.tEdgeKeyFromStr( f"{nodeID2},{nodeID1}" ),  tEdgeKey21   )
        self.assertEqual(   gu.tEdgeKeyFromStr( f"{nodeID2}:{nodeID1}" ),  tEdgeKey21   )
        self.assertEqual(   gu.tEdgeKeyFromStr( f"{nodeID2}-{nodeID1}" ),  tEdgeKey21   )
        self.assertEqual(   gu.tEdgeKeyFromStr( f"{nodeID2} {nodeID1}" ),  tEdgeKey21   )
        self.assertEqual(   gu.tEdgeKeyFromStr( f"{nodeID2} ,{nodeID1}" ), tEdgeKey21   )

    def test_tEdgeKeyToStr(self):
        self.assertEqual(  gu.tEdgeKeyToStr( tEdgeKey12 ),  f"{nodeID1} {nodeID2}" )
        self.assertEqual(  gu.tEdgeKeyToStr( tEdgeKey21 ),  f"{nodeID2} {nodeID1}" )

    def test_EdgeDisplayName(self):
        self.assertEqual(  gu.EdgeDisplayName( nodeID1, nodeID2 ),  f"{nodeID1} --> {nodeID2}" )
        self.assertEqual(  gu.EdgeDisplayName( nodeID2, nodeID1 ),  f"{nodeID2} --> {nodeID1}" )

# class TestUtilsFuncs(unittest.TestCase):

#     def test_getAgentAngle(self):

#         nxGraph = gu.loadGraphML_File( sFName = "./GraphML/magadanskaya.graphml" )

#         tEdgeKey = ('31', '34')
#         rAngle, bReverse = gu.getAgentAngle(nxGraph = nxGraph, tEdgeKey = tEdgeKey, agent_angle = 0)

if __name__ == '__main__':
    unittest.main()