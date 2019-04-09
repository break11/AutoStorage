import unittest

import sys
import os
import math
import networkx as nx

sys.path.append( os.path.abspath(os.curdir)  )

import Lib.Common.GraphUtils as gu

#доверенные значения
cos_45 = math.sqrt(2)/2
sin_45 = math.sqrt(2)/2

u_vec_0   = (1, 0)
u_vec_45  = (cos_45, sin_45)
u_vec_90  = (0, 1)
u_vec_135 = (-cos_45, sin_45)
u_vec_180 = (-1, 0)
u_vec_225 = (-cos_45, -sin_45)
u_vec_270 = (0, -1)
u_vec_315 = (cos_45, -sin_45)

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
tEdgeKey = (nodeID1, nodeID2)

x1, x2, y1, y2 = 10, -20, 30, -40

nxGraph.add_node(nodeID1, x=x1, y=y1)
nxGraph.add_node(nodeID2, x=x2, y=y2)
nxGraph.add_edge(nodeID1, nodeID2)

#тестируемые значения
test_u_vec_0   = gu.getUnitVector(10,    0)
test_u_vec_45  = gu.getUnitVector(30,   30)
test_u_vec_90  = gu.getUnitVector(0,    99)
test_u_vec_135 = gu.getUnitVector(-15,  15)
test_u_vec_180 = gu.getUnitVector(-0.4,   0)
test_u_vec_225 = gu.getUnitVector(-0.1107, -0.1107)
test_u_vec_270 = gu.getUnitVector(0,   -1.5)
test_u_vec_315 = gu.getUnitVector(2506,  -2506)

test_u_vec_from_0_deg   = gu.getUnitVector_FromDegAngle( deg_0 )
test_u_vec_from_45_deg  = gu.getUnitVector_FromDegAngle( deg_45 )
test_u_vec_from_90_deg  = gu.getUnitVector_FromDegAngle( deg_90 )
test_u_vec_from_135_deg = gu.getUnitVector_FromDegAngle( deg_135 )
test_u_vec_from_180_deg = gu.getUnitVector_FromDegAngle( deg_180 )
test_u_vec_from_225_deg = gu.getUnitVector_FromDegAngle( deg_225 )
test_u_vec_from_270_deg = gu.getUnitVector_FromDegAngle( deg_270 )
test_u_vec_from_315_deg = gu.getUnitVector_FromDegAngle( deg_315 )
test_u_vec_from_360_deg = gu.getUnitVector_FromDegAngle( deg_360 )
test_u_vec_from_540_deg = gu.getUnitVector_FromDegAngle( deg_540 )

test_0_rad_angle   = gu.getUnitVector_RadAngle( *u_vec_0 )
test_45_rad_angle  = gu.getUnitVector_RadAngle( *u_vec_45 )
test_90_rad_angle  = gu.getUnitVector_RadAngle( *u_vec_90 )
test_135_rad_angle = gu.getUnitVector_RadAngle( *u_vec_135 )
test_180_rad_angle = gu.getUnitVector_RadAngle( *u_vec_180 )
test_225_rad_angle = gu.getUnitVector_RadAngle( *u_vec_225 )
test_270_rad_angle = gu.getUnitVector_RadAngle( *u_vec_270 )
test_315_rad_angle = gu.getUnitVector_RadAngle( *u_vec_315 )

test_0_deg_angle   = gu.getUnitVector_DegAngle( *u_vec_0 )
test_45_deg_angle  = gu.getUnitVector_DegAngle( *u_vec_45 )
test_90_deg_angle  = gu.getUnitVector_DegAngle( *u_vec_90 )
test_135_deg_angle = gu.getUnitVector_DegAngle( *u_vec_135 )
test_180_deg_angle = gu.getUnitVector_DegAngle( *u_vec_180 )
test_225_deg_angle = gu.getUnitVector_DegAngle( *u_vec_225 )
test_270_deg_angle = gu.getUnitVector_DegAngle( *u_vec_270 )
test_315_deg_angle = gu.getUnitVector_DegAngle( *u_vec_315 )

test_x1, test_y1, test_x2, test_y2 = gu.getEdgeCoords (nxGraph, tEdgeKey)


#############################################################

class TestMathFuncs(unittest.TestCase):

    #вспомогательная функция сравнения двух tuple типа (float, float)
    def check_TupleVecs_IsEqual(self, vec1, vec2):
        bEqual = len(vec1) == len(vec2)
        if not bEqual: return False

        for i in range( len(vec1) ):
            bEqual = bEqual and math.isclose ( vec1[i], vec2[i], abs_tol=1e-9 )
        return bEqual

    def test_check_TupleVecs_IsEqual(self):
        self.assertTrue  (   self.check_TupleVecs_IsEqual(  u_vec_45, u_vec_45)    )
        self.assertFalse (   self.check_TupleVecs_IsEqual(  u_vec_45, u_vec_135)   )
        self.assertFalse (   self.check_TupleVecs_IsEqual( (0.1, 0.2, 0.3), (0.1, 0.2) )  )
        self.assertFalse (   self.check_TupleVecs_IsEqual( (0.1, 0.2), (0.1, 0.2, 0.3) )  )

        self.assertTrue  (   self.check_TupleVecs_IsEqual(  (1.1e-9, 1), (1.2e-9, 1) )    )
        self.assertFalse (   self.check_TupleVecs_IsEqual(  (1.1e-8, 1), (1.2e-8, 1) )    )

    ###################33
    def test_getUnitVector(self):
        self.assertTrue(   self.check_TupleVecs_IsEqual (test_u_vec_0,   u_vec_0  )   )
        self.assertTrue(   self.check_TupleVecs_IsEqual (test_u_vec_45,  u_vec_45 )   )
        self.assertTrue(   self.check_TupleVecs_IsEqual (test_u_vec_90,  u_vec_90 )   )
        self.assertTrue(   self.check_TupleVecs_IsEqual (test_u_vec_135, u_vec_135)   )
        self.assertTrue(   self.check_TupleVecs_IsEqual (test_u_vec_180, u_vec_180)   )
        self.assertTrue(   self.check_TupleVecs_IsEqual (test_u_vec_225, u_vec_225)   )
        self.assertTrue(   self.check_TupleVecs_IsEqual (test_u_vec_270, u_vec_270)   )
        self.assertTrue(   self.check_TupleVecs_IsEqual (test_u_vec_315, u_vec_315)   )

    def test_getUnitVector_RadAngle(self):
        self.assertTrue(   math.isclose (test_0_rad_angle,   0.00 * math.pi)  )
        self.assertTrue(   math.isclose (test_45_rad_angle,  0.25 * math.pi)  )
        self.assertTrue(   math.isclose (test_90_rad_angle,  0.50 * math.pi)  )
        self.assertTrue(   math.isclose (test_135_rad_angle, 0.75 * math.pi)  )
        self.assertTrue(   math.isclose (test_180_rad_angle, 1.00 * math.pi)  )
        self.assertTrue(   math.isclose (test_225_rad_angle, 1.25 * math.pi)  )
        self.assertTrue(   math.isclose (test_270_rad_angle, 1.50 * math.pi)  )
        self.assertTrue(   math.isclose (test_315_rad_angle, 1.75 * math.pi)  )

    def test_getUnitVector_DegAngle(self):
        self.assertTrue(   math.isclose (test_0_deg_angle,   0.0)    )
        self.assertTrue(   math.isclose (test_45_deg_angle,  45.0)   )
        self.assertTrue(   math.isclose (test_90_deg_angle,  90.0)   )
        self.assertTrue(   math.isclose (test_135_deg_angle, 135.0)  )
        self.assertTrue(   math.isclose (test_180_deg_angle, 180.0)  )
        self.assertTrue(   math.isclose (test_225_deg_angle, 225.0)  )
        self.assertTrue(   math.isclose (test_270_deg_angle, 270.0)  )
        self.assertTrue(   math.isclose (test_315_deg_angle, 315.0)  )

    def test_getUnitVector_FromDegAngle(self):
        self.assertTrue(   self.check_TupleVecs_IsEqual (test_u_vec_from_0_deg,   u_vec_0  )   )
        self.assertTrue(   self.check_TupleVecs_IsEqual (test_u_vec_from_45_deg,  u_vec_45 )   )
        self.assertTrue(   self.check_TupleVecs_IsEqual (test_u_vec_from_90_deg,  u_vec_90 )   )
        self.assertTrue(   self.check_TupleVecs_IsEqual (test_u_vec_from_135_deg, u_vec_135)   )
        self.assertTrue(   self.check_TupleVecs_IsEqual (test_u_vec_from_180_deg, u_vec_180)   )
        self.assertTrue(   self.check_TupleVecs_IsEqual (test_u_vec_from_225_deg, u_vec_225)   )
        self.assertTrue(   self.check_TupleVecs_IsEqual (test_u_vec_from_270_deg, u_vec_270)   )
        self.assertTrue(   self.check_TupleVecs_IsEqual (test_u_vec_from_315_deg, u_vec_315)   )
        
        self.assertTrue(   self.check_TupleVecs_IsEqual (test_u_vec_from_360_deg, u_vec_0)     )
        self.assertTrue(   self.check_TupleVecs_IsEqual (test_u_vec_from_540_deg, u_vec_180)   )


    def test_getEdgeCoords(self):
        self.assertEqual( (test_x1, test_x2, test_y1, test_y2), (x1, x2, y1, y2)  )

if __name__ == '__main__':
    unittest.main()