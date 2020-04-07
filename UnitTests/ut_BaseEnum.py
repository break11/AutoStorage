#!/usr/bin/python3.7
import unittest

import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )

from Lib.Common.BaseEnum import BaseEnum
from enum import auto

class ECustomEnum( BaseEnum ):
    One   = auto()
    Two   = auto()
    Three = auto()

    Undefined = auto()
    Default   = One

    One_Syn = One
    Two_Syn = Two

class Test_Modbus_Types(unittest.TestCase):
    def test_BaseEnum( self ):
        
        t  = ECustomEnum.One
        t1 = ECustomEnum.One_Syn

        self.assertEqual( t, t1 )
        self.assertEqual( str(t), "One" )
        self.assertEqual( f"{t1}", "One" )
        self.assertEqual( t1.toString(), "One" )

        c = ECustomEnum.fromString( "Two" )

        self.assertEqual( c, ECustomEnum.Two )
        self.assertEqual( c, ECustomEnum.Two_Syn )

        d = ECustomEnum.fromString( "Error String" )
        self.assertEqual( d, ECustomEnum.Undefined )

        self.assertNotEqual( ECustomEnum.Undefined, ECustomEnum.One )
        self.assertNotEqual( ECustomEnum.Undefined, ECustomEnum.Two )
        self.assertNotEqual( ECustomEnum.Undefined, ECustomEnum.Three )

        self.assertEqual( ECustomEnum.Default, ECustomEnum.One )

if __name__ == "__main__":
    unittest.main()