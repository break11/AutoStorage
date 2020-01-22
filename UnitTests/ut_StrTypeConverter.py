#!/usr/bin/python3.7
import unittest

import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )

from enum import Enum, auto
from Lib.Common.StrTypeConverter import CStrTypeConverter
from Lib.Common.BaseEnum import BaseEnum

class ECustomEnum( BaseEnum ):
    One   = auto()
    Two   = auto()
    Three = auto()

    Undefined = auto()
    Default   = One

class CTestType:
    def __init__( self, bVal ):
        self.bVal = bVal

    def __str__( self ): return self.toString()

    @classmethod
    def fromString( cls, sValue ): return CTestType( True ) if sValue == "True" else CTestType( False )

    def toString( self ): return str( self.bVal )


class Test_StrTypeConverter(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        CStrTypeConverter.clear()
        
    def testStdTypes( self ):
        CStrTypeConverter.registerType( int )
        CStrTypeConverter.registerType( str )
        CStrTypeConverter.registerType( float )

        a = 0
        s = CStrTypeConverter.ValToStr( a )
        self.assertEqual( s, "0" )

        b = CStrTypeConverter.ValFromStr( int, s )
        self.assertEqual( a, b )

        ######

        a = -4
        s = CStrTypeConverter.ValToStr( a )
        self.assertEqual( s, "-4" )

        b = CStrTypeConverter.ValFromStr( int, s )
        self.assertEqual( a, b )

        ######

        a = 10
        s = CStrTypeConverter.ValToStr( a )
        self.assertEqual( s, "10" )

        b = CStrTypeConverter.ValFromStr( int, s )
        self.assertEqual( a, b )

        #################

        a = 3.5
        s = CStrTypeConverter.ValToStr( a )
        self.assertEqual( s, "3.5" )

        b = CStrTypeConverter.ValFromStr( float, s )
        self.assertEqual( a, b )

        #################

        a = "test"
        s = CStrTypeConverter.ValToStr( a )
        self.assertEqual( s, "test" )

        b = CStrTypeConverter.ValFromStr( str, s )
        self.assertEqual( a, b )

        s = "test"
        b = CStrTypeConverter.ValFromStr( dict, s )
        self.assertEqual( b, None )

    def testUserTypes( self ):
        CStrTypeConverter.registerType( ECustomEnum )

        with self.assertRaises( AssertionError ):
            CStrTypeConverter.registerType( ECustomEnum )

        a = ECustomEnum.Two
        s = CStrTypeConverter.ValToStr( a )
        self.assertEqual( s, "Two" )

        b = CStrTypeConverter.ValFromStr( ECustomEnum, s )
        self.assertEqual( a, b )

        s = "NotEnumValue"
        b = CStrTypeConverter.ValFromStr( ECustomEnum, s )
        self.assertEqual( b, ECustomEnum.Undefined )

        #################

        CStrTypeConverter.registerType( CTestType )
        a = CTestType( True )
        s = CStrTypeConverter.ValToStr( a )
        self.assertEqual( s, "True" )

        b = CStrTypeConverter.ValFromStr( CTestType, s )
        self.assertEqual( b.bVal, a.bVal )

        a = CTestType( False )
        s = CStrTypeConverter.ValToStr( a )
        self.assertEqual( s, "False" )

        b = CStrTypeConverter.ValFromStr( CTestType, s )
        self.assertEqual( b.bVal, a.bVal )

if __name__ == "__main__":
    unittest.main()

