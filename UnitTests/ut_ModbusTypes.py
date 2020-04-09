#!/usr/bin/python3.7
import unittest

import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )

import Lib.Modbus.ModbusTypes as MT

class Test_Modbus_Types(unittest.TestCase):
    def test_CRegisterAddress_DI_DO( self ):
        sData = f"10{ MT.CRegisterAddress.DS }AI{ MT.CRegisterAddress.DS }51"
        Address = MT.CRegisterAddress( unitID=10, _type = MT.ERegisterType.AI, number = 51 )
        Address_test = MT.CRegisterAddress.fromString( sData )

        self.assertTrue( Address.bValid )
        self.assertEqual( Address.bValid, Address_test.bValid )
        self.assertEqual( Address._type, Address_test._type )
        self.assertEqual( Address.number, Address_test.number )
        self.assertEqual( Address.bitNum, Address_test.bitNum )
        self.assertEqual( Address.bitNum, None )

        self.assertEqual( sData, Address.toString() )

    def test_CRegisterAddress_AI_AO_with_bitNum( self ):
        sData = f"10{ MT.CRegisterAddress.DS }AI{ MT.CRegisterAddress.DS }51{ MT.CRegisterAddress.DS }3"
        Address = MT.CRegisterAddress( unitID=10, _type = MT.ERegisterType.AI, number = 51, bitNum=3 )
        Address_test = MT.CRegisterAddress.fromString( sData )

        self.assertTrue( Address.bValid )
        self.assertEqual( Address.bValid, Address_test.bValid )
        self.assertEqual( Address._type, Address_test._type )
        self.assertEqual( Address.number, Address_test.number )
        self.assertEqual( Address.bitNum, Address_test.bitNum )
        self.assertEqual( Address.bitNum, 3 )

        self.assertEqual( sData, Address.toString() )

    def test_CRegisterAddress_AI_AO_without_bitNum( self ):
        sData = f"10{ MT.CRegisterAddress.DS }AI{ MT.CRegisterAddress.DS }76"
        Address = MT.CRegisterAddress( unitID=10, _type = MT.ERegisterType.AI, number = 76 )
        Address_test = MT.CRegisterAddress.fromString( sData )

        self.assertTrue( Address.bValid )
        self.assertEqual( Address.bValid, Address_test.bValid )
        self.assertEqual( Address._type, Address_test._type )
        self.assertEqual( Address.number, Address_test.number )
        self.assertEqual( Address.bitNum, Address_test.bitNum )
        self.assertEqual( Address.bitNum, None )

        self.assertEqual( sData, Address.toString() )

if __name__ == "__main__":
    unittest.main()