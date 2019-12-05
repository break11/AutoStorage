#!/usr/bin/python3.7

import unittest
import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )

from Lib.Common.SerializedList import CStrList

class Test_SList(unittest.TestCase):
    def testTuple(self):
        t = ( "3", "4" )
        s = "3,4"
        sList = CStrList.fromTuple( t )

        self.assertEqual( sList.toString(), s )
        self.assertEqual( sList.toTuple(), t )

        sList = CStrList.fromString( s )

        self.assertEqual( sList.toString(), s )
        self.assertEqual( sList.toTuple(), t )

    def testSpace(self):
        sRes = "1,2,3"

        s = "1 2 3"
        sList = CStrList.fromString( s )
        self.assertEqual( sList.count(), 3 )
        self.assertEqual( sList.toString(), sRes )
        
        s = "1  2   3"
        sList = CStrList.fromString( s )
        self.assertEqual( sList.count(), 3 )
        self.assertEqual( sList.toString(), sRes )

    def test(self):
        sList = CStrList()

        self.assertTrue( sList.isEmpty() )

        s = "one,two,three"
        sList = CStrList.fromString( s )

        self.assertEqual( sList.count(), 3 )
        self.assertEqual( sList.toString(), s )
        self.assertEqual( str( sList ), s )

        s1 = "one , two ,three"
        sList = CStrList.fromString( s1 )
        self.assertEqual( sList.count(), 3 )
        self.assertEqual( sList.toString(), s )

        s1 = "one, two three"
        sList = CStrList.fromString( s1 )
        self.assertEqual( sList.count(), 3 )
        self.assertEqual( sList.toString(), s )

        s1 = "one:two-three"
        sList1 = CStrList.fromString( s1 )
        self.assertEqual( sList1.count(), 3 )
        self.assertEqual( sList1.toString(), s )

        self.assertEqual( sList, sList1 )

        sList1.clear()
        self.assertTrue( sList1.isEmpty() )
        self.assertFalse( sList1 )

        l = ["one","two","three"]
        self.assertEqual( sList(), l )

        for idx in range(len(l)):
            self.assertEqual( sList[idx], l[idx] )
        

if __name__ == "__main__":
    unittest.main()
