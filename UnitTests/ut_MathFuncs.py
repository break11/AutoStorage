#!/usr/bin/python3.7

import unittest

import sys
import os
import math
import networkx as nx

sys.path.append( os.path.abspath(os.curdir)  )

import Lib.Common.GraphUtils as gu
from Lib.Common.Vectors import Vector2
from Lib.Common import StorageGraphTypes as SGT

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

nxGraph = gu.loadGraphML_File( "./GraphML/math_unit_tests.graphml" )

tEdgeKey12 = ("1", "2")
tEdgeKey21 = ("2", "1")
nodeID1 = "1"
nodeID2 = "2"

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

    def test_rotate(self):
        self.assertTrue(  u_vec_0.rotate( math.pi/4 )  == u_vec_45   )
        self.assertTrue(  u_vec_45.rotate( math.pi/4 ) == u_vec_90   )
        self.assertTrue(  u_vec_90.rotate( - math.pi ) == u_vec_270  )
        self.assertTrue(  u_vec_90.rotate( 2 * math.pi )  == u_vec_90 )
        self.assertTrue(  u_vec_135.rotate( 4 * math.pi ) == u_vec_135 )

    def test_getEdgeCoords(self):
        x1, y1 = nxGraph.nodes()[nodeID1][ SGT.s_x ], nxGraph.nodes()[nodeID1][ SGT.s_y ]
        x2, y2 = nxGraph.nodes()[nodeID2][ SGT.s_x ], nxGraph.nodes()[nodeID2][ SGT.s_y ]

        test_x1, test_y1, test_x2, test_y2 = gu.getEdgeCoords (nxGraph, tEdgeKey12)
        self.assertEqual( (test_x1, test_y1, test_x2, test_y2), (x1, y1, x2, y2)  )

        test_x1, test_y1, test_x2, test_y2 = gu.getEdgeCoords (nxGraph, tEdgeKey21)
        self.assertEqual( (test_x1, test_y1, test_x2, test_y2), (x2, y2, x1, y1)  )

    def test_vecsFromNodes(self):
        nodeID = "3"
        NeighborsIDs = [ "4", "5", "6", "7", "8" ]
        compare_vecs = [ u_vec_270, u_vec_90, u_vec_0, u_vec_180, u_vec_45 ]

        test_vecs = gu.vecsFromNodes( nxGraph = nxGraph, baseNodeID = nodeID, NeighborsIDs = NeighborsIDs )
        self.assertEqual( test_vecs, compare_vecs )

        test_vecs = gu.vecsFromNodes( nxGraph = nxGraph, baseNodeID = nodeID, NeighborsIDs = [] )
        self.assertEqual( test_vecs, [] )

    def test_vecsPair_withMaxAngle(self):

        vecs = [ u_vec_0, u_vec_45 ]        
        self.assertEqual ( frozenset( gu.vecsPair_withMaxAngle( vecs ) ), frozenset( (u_vec_0, u_vec_45) ) )

        vecs = [ u_vec_0, u_vec_45, u_vec_90]
        self.assertEqual ( frozenset( gu.vecsPair_withMaxAngle( vecs ) ), frozenset( (u_vec_0, u_vec_90) ) )

        vecs = [ u_vec_90, u_vec_135, u_vec_180, u_vec_225, u_vec_270 ]
        self.assertEqual ( frozenset( gu.vecsPair_withMaxAngle( vecs ) ), frozenset( (u_vec_90, u_vec_270) ) )

        vecs = [ u_vec_45, u_vec_90, u_vec_135, u_vec_180, u_vec_225 ]
        self.assertEqual ( frozenset( gu.vecsPair_withMaxAngle( vecs ) ), frozenset( (u_vec_45, u_vec_225) ) )

        vecs = []
        self.assertEqual ( gu.vecsPair_withMaxAngle( vecs ), None )

        vecs = [ u_vec_0 ]
        self.assertEqual ( gu.vecsPair_withMaxAngle( vecs ), None )

    def test_rotateToRightSector(self):

        vec = gu.rotateToRightSector( u_vec_0 )
        self.assertEqual( vec, u_vec_0 )

        vec = gu.rotateToRightSector( u_vec_45 )
        self.assertEqual( vec, u_vec_45 )
        
        vec = gu.rotateToRightSector( u_vec_90 )
        self.assertEqual( vec, u_vec_270 )

        vec = gu.rotateToRightSector( u_vec_135 )
        self.assertEqual( vec, u_vec_315 )

        vec = gu.rotateToRightSector( u_vec_180 )
        self.assertEqual( vec, u_vec_0 )

        vec = gu.rotateToRightSector( u_vec_225 )
        self.assertEqual( vec, u_vec_225 )
        
        vec = gu.rotateToRightSector( u_vec_270 )
        self.assertEqual( vec, u_vec_270 )

        vec = gu.rotateToRightSector( u_vec_315 )
        self.assertEqual( vec, u_vec_315 )

    def test_rotateToLeftSector(self):

        vec = gu.rotateToLeftSector( u_vec_0 )
        self.assertEqual( vec, u_vec_180 )

        vec = gu.rotateToLeftSector( u_vec_45 )
        self.assertEqual( vec, u_vec_45 )
        
        vec = gu.rotateToLeftSector( u_vec_90 )
        self.assertEqual( vec, u_vec_90 )

        vec = gu.rotateToLeftSector( u_vec_135 )
        self.assertEqual( vec, u_vec_135 )

        vec = gu.rotateToLeftSector( u_vec_180 )
        self.assertEqual( vec, u_vec_180 )

        vec = gu.rotateToLeftSector( u_vec_225 )
        self.assertEqual( vec, u_vec_225 )
        
        vec = gu.rotateToLeftSector( u_vec_270 )
        self.assertEqual( vec, u_vec_90 )

        vec = gu.rotateToLeftSector( u_vec_315 )
        self.assertEqual( vec, u_vec_135 )

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
