#!/usr/bin/python3.7
import unittest

import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )

from enum import Enum, auto
from Lib.Common.StrTypeConverter import CStrTypeConverter
from Lib.Common.Utils import EnumFromString, EnumToString

class ECustomEnum( Enum ):
    One   = auto()
    Two   = auto()
    Three = auto()

    @staticmethod
    def fromString( sType ): return EnumFromString( ECustomEnum, sType, ECustomEnum.One )

    def toString( self ): return EnumToString( self )

class Test_StrTypeConverter(unittest.TestCase):
    def testStdTypes( self ):
        a = 0
        s = CStrTypeConverter.ValToStr( a )
        self.assertEqual( s, "i0" )

        b = CStrTypeConverter.ValFromStr( s )
        self.assertEqual( a, b )

        ######

        a = -4
        s = CStrTypeConverter.ValToStr( a )
        self.assertEqual( s, "i-4" )

        b = CStrTypeConverter.ValFromStr( s )
        self.assertEqual( a, b )

        ######

        a = 10
        s = CStrTypeConverter.ValToStr( a )
        self.assertEqual( s, "i10" )

        b = CStrTypeConverter.ValFromStr( s )
        self.assertEqual( a, b )

        #################

        a = 3.5
        s = CStrTypeConverter.ValToStr( a )
        self.assertEqual( s, "f3.5" )

        b = CStrTypeConverter.ValFromStr( s )
        self.assertEqual( a, b )

        #################

        a = "test"
        s = CStrTypeConverter.ValToStr( a )
        self.assertEqual( s, "stest" )

        b = CStrTypeConverter.ValFromStr( s )
        self.assertEqual( a, b )

        s = "atest"
        b = CStrTypeConverter.ValFromStr( s )
        self.assertEqual( b, None )

    def testUserTypes( self ):
        CStrTypeConverter.registerUserType( "a", ECustomEnum )

        with self.assertRaises( AssertionError ):
            CStrTypeConverter.registerUserType( "a", ECustomEnum )

        a = ECustomEnum.Two
        s = CStrTypeConverter.ValToStr( a )
        self.assertEqual( s, "aTwo" )

        b = CStrTypeConverter.ValFromStr( s )
        self.assertEqual( a, b )

        s = "bTwo"
        b = CStrTypeConverter.ValFromStr( s )
        self.assertEqual( b, None )

if __name__ == "__main__":
    unittest.main()

