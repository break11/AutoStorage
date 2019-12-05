#!/usr/bin/python3.7
import unittest

import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )

from Lib.Common.StrConsts import genSplitPattern

class Test_Diff_Utils(unittest.TestCase):
    def test_genSplitPattern(self):
        s = " , | ,|, |,"
        sTest = genSplitPattern( "," )
        self.assertEqual( s, sTest )

        g = f"{s}| : | :|: |:"
        sTest = genSplitPattern( ",", ":" )
        self.assertEqual( g, sTest )

        s = " \| | \||\| |\|"
        sTest = genSplitPattern( "\|" )
        self.assertEqual( s, sTest )

        s = " , | ,|, |,|   |  |  | | : | :|: |:| - | -|- |-"
        sTest = genSplitPattern( ",", " ", ":", "-" )
        self.assertEqual( s, sTest )

if __name__ == "__main__":
    unittest.main()