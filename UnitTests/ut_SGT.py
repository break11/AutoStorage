#!/usr/bin/python3.7
import unittest

import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )

import Lib.GraphEntity.StorageGraphTypes as SGT

class Test_SGM_Funcs(unittest.TestCase):
    def test_SEdgePlace(self):
        sData = "1|2|100"
        edgePlace = SGT.SEdgePlace.fromString( sData )
        self.assertEqual( edgePlace.toString(), sData )

        sData1 = "1 |2 | 100"
        edgePlace = SGT.SEdgePlace.fromString( sData1 )
        self.assertEqual( edgePlace.toString(), sData )

        sData = "1|2|string"
        edgePlace = SGT.SEdgePlace.fromString( sData )
        self.assertFalse( edgePlace.isValid() )

        sData = "ErrorEdgePlace"
        edgePlace = SGT.SEdgePlace.fromString( sData )
        self.assertFalse( edgePlace.isValid() )

    def test_SNodePlace(self):
        sData = "ChargeNode01|Right"
        nodePlace = SGT.SNodePlace.fromString( sData )
        self.assertEqual( nodePlace.toString(), sData )

        sData = "14|Left"
        nodePlace = SGT.SNodePlace.fromString( sData )
        self.assertEqual( nodePlace.toString(), sData )

        sData2 = "14|L"
        nodePlace2 = SGT.SNodePlace.fromString( sData2 )
        self.assertEqual( nodePlace, nodePlace2 )
        self.assertEqual( nodePlace.nodeID, "14" )
        self.assertEqual( nodePlace.side, SGT.ESide.Left )
        self.assertTrue( nodePlace.isValid() )

        sData2 = "14 |L"
        nodePlace2 = SGT.SNodePlace.fromString( sData2 )
        self.assertEqual( nodePlace, nodePlace2 )

        sData2 = "14| L"
        nodePlace2 = SGT.SNodePlace.fromString( sData2 )
        self.assertEqual( nodePlace, nodePlace2 )

        sData2 = "14 | L"
        nodePlace2 = SGT.SNodePlace.fromString( sData2 )
        self.assertEqual( nodePlace, nodePlace2 )

        sData = "ErrorNodePlace"
        nodePlace = SGT.SNodePlace.fromString( sData )
        self.assertFalse( nodePlace.isValid() )

        sData = "13 | ABC"
        nodePlace = SGT.SNodePlace.fromString( sData )
        self.assertFalse( nodePlace.isValid() )

if __name__ == "__main__":
    unittest.main()