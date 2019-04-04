import unittest

import sys
import os
import math

sys.path.append( os.path.abspath(os.curdir)  )

import Lib.Common.GraphUtils as gu

cos_45 = math.sqrt(2)/2
sin_45 = math.sqrt(2)/2

test_u_vec_0   = gu.getUnitVector(10,    0)
test_u_vec_45  = gu.getUnitVector(30,   30)
test_u_vec_90  = gu.getUnitVector(0,    99)
test_u_vec_135 = gu.getUnitVector(-15,  15)
test_u_vec_180 = gu.getUnitVector(-0.4,   0)
test_u_vec_225 = gu.getUnitVector(-0.1107, -0.1107)
test_u_vec_270 = gu.getUnitVector(0,   -1.5)
test_u_vec_315 = gu.getUnitVector(2506,  -2506)

u_vec_0   = (1, 0)
u_vec_45  = (cos_45, sin_45)
u_vec_90  = (0, 1)
u_vec_135 = (-cos_45, sin_45)
u_vec_180 = (-1, 0)
u_vec_225 = (-cos_45, -sin_45)
u_vec_270 = (0, -1)
u_vec_315 = (cos_45, -sin_45)

class TestMathFuncs(unittest.TestCase):

    def check_TupleVecs_IsEqual(self, vec1, vec2):
        return math.isclose ( vec1[0], vec2[0] ) and math.isclose( vec1[1], vec2[1] )

    def test_check_TupleVecs_IsEqual(self):
        self.assertTrue  ( self.check_TupleVecs_IsEqual(u_vec_45, u_vec_45)  )
        self.assertFalse ( self.check_TupleVecs_IsEqual(u_vec_45, u_vec_135) )

    def test_getUnitVector(self):
        self.assertTrue(   self.check_TupleVecs_IsEqual (test_u_vec_0,   u_vec_0  )   )
        self.assertTrue(   self.check_TupleVecs_IsEqual (test_u_vec_45,  u_vec_45 )   )
        self.assertTrue(   self.check_TupleVecs_IsEqual (test_u_vec_90,  u_vec_90 )   )
        self.assertTrue(   self.check_TupleVecs_IsEqual (test_u_vec_135, u_vec_135)   )
        self.assertTrue(   self.check_TupleVecs_IsEqual (test_u_vec_180, u_vec_180)   )
        self.assertTrue(   self.check_TupleVecs_IsEqual (test_u_vec_225, u_vec_225)   )
        self.assertTrue(   self.check_TupleVecs_IsEqual (test_u_vec_270, u_vec_270)   )
        self.assertTrue(   self.check_TupleVecs_IsEqual (test_u_vec_315, u_vec_315)   )

if __name__ == '__main__':
    unittest.main()