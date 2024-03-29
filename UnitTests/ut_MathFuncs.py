#!/usr/bin/python3.7

import unittest

import sys
import os
import math
import networkx as nx

sys.path.append( os.path.abspath(os.curdir)  )

import Lib.Common.GraphUtils as gu
from Lib.Common.Vectors import Vector2
from Lib.GraphEntity import StorageGraphTypes as SGT
from Lib.GraphEntity.StorageGraphTypes import SGA

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

nxGraph         = gu.loadGraphML_File( "./UnitTests/math_unit_tests.graphml" )
SGT.prepareGraphProps( nxGraph )

nxGraph_mag_ext = gu.loadGraphML_File( "./UnitTests/magadanskaya_ext_unit_tests.graphml" )
SGT.prepareGraphProps( nxGraph_mag_ext )

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
        x1, y1 = nxGraph.nodes()[nodeID1][ SGA.x ], nxGraph.nodes()[nodeID1][ SGA.y ]
        x2, y2 = nxGraph.nodes()[nodeID2][ SGA.x ], nxGraph.nodes()[nodeID2][ SGA.y ]

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
        self.assertEqual( vec, u_vec_45 )
        
        vec = gu.rotateToRightSector( u_vec_270 )
        self.assertEqual( vec, u_vec_270 )

        vec = gu.rotateToRightSector( u_vec_315 )
        self.assertEqual( vec, u_vec_315 )

    def test_rotateToLeftSector(self):

        vec = gu.rotateToLeftSector( u_vec_0 )
        self.assertEqual( vec, u_vec_180 )

        vec = gu.rotateToLeftSector( u_vec_45 )
        self.assertEqual( vec, u_vec_225 )
        
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

    def test_getAgentAngle(self):

        tEdgeKey = ("29", "30") # Narrow edge

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 0.0)
        self.assertEqual(    (angle, bReverse), (0.0, False)    )

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 180.0)
        self.assertEqual(    (angle, bReverse), (180.0, True)    )

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 90.0)
        self.assertEqual(    (angle, bReverse), (90.0, None)    )

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 30.0)
        self.assertEqual(    (angle, bReverse), (0.0, False)    )

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 390.0)
        self.assertEqual(    (angle, bReverse), (0.0, False)    )

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 330.0)
        self.assertEqual(    (angle, bReverse), (0.0, False)    )

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 160.0)
        self.assertEqual(    (angle, bReverse), (180.0, True)    )
        
        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 210.0)
        self.assertEqual(    (angle, bReverse), (180.0, True)    )

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 45.0)
        self.assertEqual(    (angle, bReverse), (0.0, False)    )

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 315.0)
        self.assertEqual(    (angle, bReverse), (315.0, None)    )

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 80.0)
        self.assertEqual(    (angle, bReverse), (80.0, None)    )

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 270.0)
        self.assertEqual(    (angle, bReverse), (270.0, None)    )


        tEdgeKey = ("34", "35") # Wide edge

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 0.0)
        self.assertEqual(    (angle, bReverse), (0.0, False)    )

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 180.0)
        self.assertEqual(    (angle, bReverse), (180.0, True)    )

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 90.0)
        self.assertEqual(    (angle, bReverse), (90.0, None)    )

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 30.0)
        self.assertEqual(    (angle, bReverse), (0.0, False)    )

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 330.0)
        self.assertEqual(    (angle, bReverse), (0.0, False)    )

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 160.0)
        self.assertEqual(    (angle, bReverse), (180.0, True)    )
        
        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 210.0)
        self.assertEqual(    (angle, bReverse), (180.0, True)    )

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 45.01)
        self.assertEqual(    (angle, bReverse), (45.01, None)    ) # из-за ошибок точности для широкого рельса берём величину чуть больше 45

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 315.0)
        self.assertEqual(    (angle, bReverse), (315.0, None)    )

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 80.0)
        self.assertEqual(    (angle, bReverse), (80.0, None)    )

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 270.0)
        self.assertEqual(    (angle, bReverse), (270, None)    )


        tEdgeKey = ("11", "10")
        edge_angle, reverse_edge_angle = 14.76, 194.76
        edge_angle_45  = 14.76 + 45.01
        edge_angle_315 = 14.76 + 314.99
        edge_angle_80  = 14.76 + 80.0
        edge_angle_270 = 14.76 + 270.0
       
        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 0.0)
        self.assertEqual(    (round(angle, 2), bReverse), (edge_angle, False)    )

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 180.0)
        self.assertEqual(    (round(angle, 2), bReverse), (reverse_edge_angle, True)    )

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 90.0)
        self.assertEqual(    (angle, bReverse), (90.0, None)    )

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 30.0)
        self.assertEqual(    (round(angle, 2), bReverse), (edge_angle, False)    )

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 330.0)
        self.assertEqual(    (round(angle, 2), bReverse), (edge_angle, False)    )

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 160.0)
        self.assertEqual(    (round(angle, 2), bReverse), (reverse_edge_angle, True)    )
        
        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = 210.0)
        self.assertEqual(    (round(angle, 2), bReverse), (reverse_edge_angle, True)    )

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = edge_angle_45)
        self.assertEqual(    (angle, bReverse), (edge_angle_45, None)    )

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = edge_angle_315)
        self.assertEqual(    (angle, bReverse), (edge_angle_315, None)    )

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = edge_angle_80)
        self.assertEqual(    (angle, bReverse), (edge_angle_80, None)    )

        angle, bReverse = gu.getAgentAngle(nxGraph = nxGraph_mag_ext, tEdgeKey = tEdgeKey, agent_angle = edge_angle_270)
        self.assertEqual(    (angle, bReverse), (edge_angle_270, None)    )

    def test_closestCycleNode(self):
        cycle = ["20", "19", "18", "17", "16", "24", "25", "23", "22", "21"]
        
        nodeID = gu.closestCycleNode( nxGraph_mag_ext, "38", cycle )
        self.assertEqual( nodeID, "20" )

        nodeID = gu.closestCycleNode( nxGraph_mag_ext, "10", cycle )
        self.assertEqual( nodeID, "16" )

        nodeID = gu.closestCycleNode( nxGraph_mag_ext, "26", cycle )
        self.assertEqual( nodeID, "25" )

        nodeID = gu.closestCycleNode( nxGraph_mag_ext, "18", cycle )
        self.assertEqual( nodeID, "18" )

        nodeID = gu.closestCycleNode( nxGraph_mag_ext, "20", cycle )
        self.assertEqual( nodeID, "20" )

        nodeID = gu.closestCycleNode( nxGraph_mag_ext, "29", cycle )
        self.assertEqual( nodeID, "20" )

    def test_remapCycle(self):
        cycle = ["20", "19", "18", "17", "16", "24", "25", "23", "22", "21"]

        remaped_cycle = ["16", "24", "25", "23", "22", "21", "20", "19", "18", "17"]
        test_cycle = gu.remapCycle( "16", cycle )
        self.assertEqual( remaped_cycle, test_cycle )

        remaped_cycle = ["23", "22", "21", "20", "19", "18", "17", "16", "24", "25"]
        test_cycle = gu.remapCycle( "23", cycle )
        self.assertEqual( remaped_cycle, test_cycle )

    def test_mergeCycleWithPath(self):
        #################################################### 
        simple_path = [ 0,1,2,3,4,5 ]
        cycle =  [1,2,3,71,70]
        cycle_reverse =  [1,70,71,3,2]  

        merged = [0, 1, 2, 3, 71, 70, 1, 2, 3, 4, 5]
        test_merged = gu.mergeCycleWithPath( cycle, simple_path )
        self.assertEqual(  test_merged, merged  )
        
        merged = [0, 1, 70, 71, 3, 4, 5]
        test_merged = gu.mergeCycleWithPath( cycle_reverse, simple_path )
        self.assertEqual(  test_merged, merged  )
        ####################################################
        simple_path = [ 3,4,5 ]

        merged = [3, 71, 70, 1, 2, 3, 4, 5]
        test_merged = gu.mergeCycleWithPath( cycle, simple_path )
        self.assertEqual( test_merged, merged )

        merged = [3, 2, 1, 70, 71, 3, 4, 5]
        test_merged = gu.mergeCycleWithPath( cycle_reverse, simple_path )
        self.assertEqual( test_merged, merged )
        ####################################################
        simple_path = [ 4,5 ]

        merged = None
        test_merged = gu.mergeCycleWithPath( cycle, simple_path )
        self.assertEqual( test_merged, merged )

    def test_pathWeight(self):
        path = [ "20", "29", "30", "31" ]
        weight = 550 + 2760 + 712

        test_weight = gu.pathWeight( nxGraph_mag_ext, path )
        self.assertEqual( weight, test_weight )

        test_weight = gu.pathWeight( nxGraph_mag_ext, path, weight=None )
        self.assertEqual( 3, test_weight )


    def test_shortestNodesRoute(self):
        
        ############# Варианты без необходимости рассчета разворота (кратчайший путь даст неоходимий поворот) ############
        nodes_route = ["26", "25", "23", "22", "21", "20", "29", "30", "31", "34", "35", "36", "37", "38", "39", "40"]

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("26", "25"), agentAngle = 90.0, targetNode = "40", targetSide = None )
        self.assertEqual ( nodes_route, test_nodes_route )
        
        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("26", "25"), agentAngle = 270.0, targetNode = "40", targetSide = None )
        self.assertEqual ( nodes_route, test_nodes_route )

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("26", "25"), agentAngle = 90.0, targetNode = "40", targetSide = SGT.ESide.Right )
        self.assertEqual ( nodes_route, test_nodes_route )

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("26", "25"), agentAngle = 270.0, targetNode = "40", targetSide = SGT.ESide.Left )
        self.assertEqual ( nodes_route, test_nodes_route )

        ################################# Рассчет разворота, кратчайший путь частично проходит через цикл ##################
        nodes_route = ["26", "25", "24", "16", "17", "18", "19", "20", "29", "30", "31", "34", "35", "36", "37", "38", "39", "40"]

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("26", "25"), agentAngle = 90.0, targetNode = "40", targetSide = SGT.ESide.Left )
        self.assertEqual ( nodes_route, test_nodes_route )

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("26", "25"), agentAngle = 270.0, targetNode = "40", targetSide = SGT.ESide.Right )
        self.assertEqual ( nodes_route, test_nodes_route )

        ##################  Рассчет разворота, кратчайший путь стартует с цикла и частично проходит через цикл ##############
        
        # case 1
        nodes_route = ["25", "24", "16", "17", "18", "19", "20", "29", "30", "31", "34", "35", "36", "37", "38", "39", "40"]

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("25", "24"), agentAngle = 90.0, targetNode = "40", targetSide = SGT.ESide.Left )
        self.assertEqual ( nodes_route, test_nodes_route )

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("25", "24"), agentAngle = 270.0, targetNode = "40", targetSide = SGT.ESide.Right )
        self.assertEqual ( nodes_route, test_nodes_route )

        # case 2
        nodes_route = ["19", "18", "17", "16", "24", "25", "23", "22", "21", "20", "29", "30", "31", "34", "35", "36", "37", "38", "39", "40"]

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("19", "18"), agentAngle = 0.0, targetNode = "40", targetSide = SGT.ESide.Left )
        self.assertEqual ( nodes_route, test_nodes_route )

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("19", "18"), agentAngle = 180.0, targetNode = "40", targetSide = SGT.ESide.Right )
        self.assertEqual ( nodes_route, test_nodes_route )


        ###### Без разворота, кратчайший путь стартует с цикла и эта нода - единственное пересечение с циклом #######
        nodes_route = ["20", "29", "30", "31", "34", "35", "36", "37", "38", "39", "40"]

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("20", "29"), agentAngle = 180.0, targetNode = "40", targetSide = SGT.ESide.Left )
        self.assertEqual ( nodes_route, test_nodes_route )

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("20", "29"), agentAngle = 0.0, targetNode = "40", targetSide = SGT.ESide.Right )
        self.assertEqual ( nodes_route, test_nodes_route )

        ###### Рассчет разворота, кратчайший путь стартует с цикла и эта нода - единственное пересечение с циклом #######
        nodes_route_1 = ["20", "19", "18", "17", "16", "24", "25", "23", "22", "21", "20", "29", "30", "31", "34", "35", "36", "37", "38", "39", "40"]
        nodes_route_2 = ["20", "21", "22", "23", "25", "24", "16", "17", "18", "19", "20", "29", "30", "31", "34", "35", "36", "37", "38", "39", "40"]

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("20", "19"), agentAngle = 0.0, targetNode = "40", targetSide = SGT.ESide.Left )
        self.assertIn ( test_nodes_route, [ nodes_route_1, nodes_route_2 ] )

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("20", "21"), agentAngle = 180.0, targetNode = "40", targetSide = SGT.ESide.Right )
        self.assertIn ( test_nodes_route, [ nodes_route_1, nodes_route_2 ] )


        ########################  Рассчет разворота, кратчайший путь не проходит через цикл #############################
        # case 1
        nodes_route_1 = ["44", "43", "38", "37", "36", "35", "34", "31", "30", "29", "20", "19", "18", "17", "16", "24", "25", "23", "22", "21", "20", "29", "30", "31", "34", "35", "36", "37", "38", "39", "40"]
        nodes_route_2 = ["44", "43", "38", "37", "36", "35", "34", "31", "30", "29", "20", "21", "22", "23", "25", "24", "16", "17", "18", "19", "20", "29", "30", "31", "34", "35", "36", "37", "38", "39", "40"]

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("44", "43"), agentAngle = 0.0, targetNode = "40", targetSide = SGT.ESide.Left )
        self.assertIn ( test_nodes_route, [ nodes_route_1, nodes_route_2 ] )

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("44", "43"), agentAngle = 180.0, targetNode = "40", targetSide = SGT.ESide.Right )
        self.assertIn ( test_nodes_route, [ nodes_route_1, nodes_route_2 ] )

        # case 2
        nodes_route_1 = ["29", "20", "19", "18", "17", "16", "24", "25", "23", "22", "21", "20", "29"]
        nodes_route_2 = ["29", "20", "21", "22", "23", "25", "24", "16", "17", "18", "19", "20", "29"]

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("29", "20"), agentAngle = 0.0, targetNode = "29", targetSide = SGT.ESide.Left )
        self.assertIn ( test_nodes_route, [ nodes_route_1, nodes_route_2 ] )

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("29", "20"), agentAngle = 180.0, targetNode = "29", targetSide = SGT.ESide.Right )
        self.assertIn ( test_nodes_route, [ nodes_route_1, nodes_route_2 ] )

        # case 3
        nodes_route_1 = ["61", "62", "77", "78", "68", "76", "67", "95", "66", "71", "70", "64", "96", "69", "75", "62", "61", "54", "33", "31", "34", "35", "36", "37", "38", "39", "40"]
        nodes_route_2 = ["61", "62", "75", "69", "96", "64", "70", "71", "66", "95", "67", "76", "68", "78", "77", "62", "61", "54", "33", "31", "34", "35", "36", "37", "38", "39", "40"]

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("61", "62"), agentAngle = 0.0, targetNode = "40", targetSide = SGT.ESide.Left )
        self.assertIn ( test_nodes_route, [ nodes_route_1, nodes_route_2 ] )

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("61", "62"), agentAngle = 180.0, targetNode = "40", targetSide = SGT.ESide.Right )
        self.assertIn ( test_nodes_route, [ nodes_route_1, nodes_route_2 ] )

        ################## Стартовая и целевая ноды совпадают, разворот не требуется #####################################
        nodes_route = ["29"]

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("29", "20"), agentAngle = 0.0, targetNode = "29", targetSide = SGT.ESide.Right )
        self.assertEqual ( test_nodes_route, nodes_route )

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("29", "20"), agentAngle = 180.0, targetNode = "29", targetSide = SGT.ESide.Left )
        self.assertEqual ( test_nodes_route, nodes_route )

        ###################  Стартовая и целевая ноды совпадают, разворот #################################################
        nodes_route_1 = ['40', '39', '38', '37', '36', '35', '34', '31', '30', '29', '20', '21', '22', '23', '25', '24', '16', '17', '18', '19', '20', '29', '30', '31', '34', '35', '36', '37', '38', '39', '40']
        nodes_route_2 = ['40', '39', '38', '37', '36', '35', '34', '31', '30', '29', '20', '19', '18', '17', '16', '24', '25', '23', '22', '21', '20', '29', '30', '31', '34', '35', '36', '37', '38', '39', '40']

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("40", "39"), agentAngle = 0.0, targetNode = "40", targetSide = SGT.ESide.Left )
        self.assertIn ( test_nodes_route, [ nodes_route_1, nodes_route_2 ] )

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("40", "39"), agentAngle = 180.0, targetNode = "40", targetSide = SGT.ESide.Right )
        self.assertIn ( test_nodes_route, [ nodes_route_1, nodes_route_2 ] )

        #############  Разворот с использованием однонаправленного цикла, кратчайший маршрут пересекается с циклом  #######
        nodes_route = ["83", "90", "89", "53", "86", "79", "80", "81", "82", "87", "83", "90", "89", "53", "52", "51", "50", "49", "48", "47", "46", "45", "44", "43", "38", "39", "40"]

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("83", "90"), agentAngle = 0.0, targetNode = "40", targetSide = SGT.ESide.Left )
        self.assertEqual ( test_nodes_route, nodes_route )

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("83", "90"), agentAngle = 180.0, targetNode = "40", targetSide = SGT.ESide.Right )
        self.assertEqual ( test_nodes_route, nodes_route )

        #################### Стартовая и конечная нода на узком рельсе ####################
        nodes_route = ["29", "20", "21", "22", "23", "25", "26" ]

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("29", "20"), agentAngle = 180.0, targetNode = "26", targetSide = SGT.ESide.Left )
        self.assertEqual ( test_nodes_route, nodes_route )

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("29", "20"), agentAngle = 0.0, targetNode = "26", targetSide = SGT.ESide.Right )
        self.assertEqual ( test_nodes_route, nodes_route )

        nodes_route = ['29', '20', '19', '18', '17', '16', '24', '25', '26']
        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("29", "20"), agentAngle = 0.0, targetNode = "26", targetSide = SGT.ESide.Left )
        self.assertEqual ( test_nodes_route, nodes_route )

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("29", "20"), agentAngle = 180.0, targetNode = "26", targetSide = SGT.ESide.Right )
        self.assertEqual ( test_nodes_route, nodes_route )

        ##################### Стартовая и конечная нода на узком рельсе, конечной нода на кривой ######################

        nodes_route = ["29", "20", "19", "18", "17"]
        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("29", "20"), agentAngle = 180.0, targetNode = "17", targetSide = None )
        self.assertEqual ( test_nodes_route, nodes_route )

        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("29", "20"), agentAngle = 180.0, targetNode = "17", targetSide = SGT.ESide.Right )
        self.assertEqual ( test_nodes_route, nodes_route )

        nodes_route = ['29', '20', '21', '22', '23', '25', '24', '16', '17']
        test_wight, test_nodes_route = gu.shortestNodesRoute( nxGraph_mag_ext, agentEdge = ("29", "20"), agentAngle = 180.0, targetNode = "17", targetSide = SGT.ESide.Left )
        self.assertEqual ( test_nodes_route, nodes_route )


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

    def test_nodeByPos(self):
        self.assertEqual( gu.nodeByPos( nxGraph, tEdgeKey12, 0 ),   "1" )
        self.assertEqual( gu.nodeByPos( nxGraph, tEdgeKey12, 500 ), "2" )
        self.assertEqual( gu.nodeByPos( nxGraph, tEdgeKey12, 51 ),  None )
        self.assertEqual( gu.nodeByPos( nxGraph, tEdgeKey12, 449 ), None )
        self.assertEqual( gu.nodeByPos( nxGraph, tEdgeKey12, 4,   allowOffset=5 ), "1" )
        self.assertEqual( gu.nodeByPos( nxGraph, tEdgeKey12, 496, allowOffset=5 ), "2" )
        self.assertEqual( gu.nodeByPos( nxGraph, tEdgeKey12, 6,   allowOffset=5 ), None )
        self.assertEqual( gu.nodeByPos( nxGraph, tEdgeKey12, 494, allowOffset=5 ), None )

    def test_isOnNode(self):
        self.assertEqual( gu.isOnNode( nxGraph, tEdgeKey12, 0,   _nodeTypes = { SGT.ENodeTypes.RailPoint } ), True )
        self.assertEqual( gu.isOnNode( nxGraph, tEdgeKey12, 0,   _nodeTypes = { SGT.ENodeTypes.PowerStation } ), False )
        self.assertEqual( gu.isOnNode( nxGraph, tEdgeKey12, 500, _nodeTypes = { SGT.ENodeTypes.RailPoint } ), True )
        self.assertEqual( gu.isOnNode( nxGraph, tEdgeKey12, 500, _nodeTypes = { SGT.ENodeTypes.PowerStation } ), False )

        self.assertEqual( gu.isOnNode( nxGraph, tEdgeKey12, 0,   _nodeID="1", _nodeTypes = { SGT.ENodeTypes.RailPoint } ), True )
        self.assertEqual( gu.isOnNode( nxGraph, tEdgeKey12, 0,   _nodeID="1", _nodeTypes = { SGT.ENodeTypes.PowerStation } ), False )
        self.assertEqual( gu.isOnNode( nxGraph, tEdgeKey12, 500, _nodeID="2", _nodeTypes = { SGT.ENodeTypes.RailPoint } ), True )
        self.assertEqual( gu.isOnNode( nxGraph, tEdgeKey12, 500, _nodeID="2", _nodeTypes = { SGT.ENodeTypes.PowerStation } ), False )

        self.assertEqual( gu.isOnNode( nxGraph, tEdgeKey12, 500, _nodeID="1", _nodeTypes = { SGT.ENodeTypes.PowerStation } ), False )
        self.assertEqual( gu.isOnNode( nxGraph, tEdgeKey12, 0,   _nodeID="2", _nodeTypes = { SGT.ENodeTypes.PowerStation } ), False )

    def test_randomNodes(self):
        _nodeTypes, count = { SGT.ENodeTypes.StoragePoint }, 4
        nodes = gu.randomNodes( nxGraph_mag_ext, _nodeTypes, count = count )
        bTypes = map( lambda nodeID: gu.nodeType( nxGraph_mag_ext, nodeID ) in _nodeTypes, nodes )
        
        self.assertTrue( all(bTypes) )
        self.assertTrue( len(nodes) == count )

        #####################################################################################
        _nodeTypes, count = { SGT.ENodeTypes.RailPoint, SGT.ENodeTypes.PowerStation }, 2
        nodes = gu.randomNodes( nxGraph_mag_ext, _nodeTypes, count = count )
        bTypes = map( lambda nodeID: gu.nodeType( nxGraph_mag_ext, nodeID ) in _nodeTypes, nodes )
        
        self.assertTrue( all(bTypes) )
        self.assertTrue( len(nodes) == count )

        #####################################################################################
        _nodeTypes, count = { SGT.ENodeTypes.PowerStation }, 2
        nodes = gu.randomNodes( nxGraph_mag_ext, _nodeTypes, count = count )

        self.assertTrue( len(nodes) == count )
        self.assertNotEqual( nodes[0], nodes[1] )

        #####################################################################################
        _nodeTypes, count = { SGT.ENodeTypes.PowerStation }, 10
        nodes = gu.randomNodes( nxGraph_mag_ext, _nodeTypes, count = count, allowDuplicates=True )

        self.assertTrue( len(nodes) == count )

        #####################################################################################
        _nodeTypes = { SGT.ENodeTypes.StoragePoint }
        storage_points = ['2', '4', '44', '45', '46', '5', '6', '7', '70', '71', '8', '80', '81', '9']
        nodes = gu.randomNodes( nxGraph_mag_ext, _nodeTypes )

        self.assertSequenceEqual( storage_points, sorted(nodes) )        
        self.assertEqual( len(nodes), 14 )

    def test_extendPath_ifCrossTooClose(self):
        path = [ "37", "38", "43", "44" ]
        extended_path = [ "37", "38", "43", "44", "45", "44" ]

        test_extended_path = gu.extendPath_ifCrossTooClose( nxGraph = nxGraph_mag_ext, nodes_route = path )
        self.assertEqual( test_extended_path, path )

        test_extended_path = gu.extendPath_ifCrossTooClose( nxGraph = nxGraph_mag_ext, nodes_route = path, length_treshhold=1500 )
        self.assertEqual( test_extended_path, extended_path )

if __name__ == "__main__":
    unittest.main()
