#!/usr/bin/python3.7

import unittest
import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )

from Lib.BoxEntity.BoxAddress import CBoxAddress, EBoxAddressType
import Lib.GraphEntity.StorageGraphTypes as SGT

class Test_CBoxAddress(unittest.TestCase):

    def test(self):
        sData = "Undefined=25|Left|555"

        addr = CBoxAddress( EBoxAddressType.Undefined, data = "25|Left|555" )
        addr_test = CBoxAddress.fromString( sData )

        self.assertEqual( addr, addr_test )
        self.assertEqual( addr.toString(), sData )
        self.assertEqual( addr_test.toString(), sData )

        ##################################################################################################
        sData = "OnNode=25|Left"
        addr  = CBoxAddress( EBoxAddressType.OnNode, data = SGT.SNodePlace( "25", SGT.ESide.Left ) )
        addr1 = CBoxAddress( EBoxAddressType.OnNode, data = SGT.SNodePlace.fromString( "25|Left" ) )
        addr_test = CBoxAddress.fromString( sData )

        self.assertEqual( addr, addr1 )
        self.assertEqual( addr, addr_test )
        self.assertEqual( addr.toString(), sData )
        self.assertEqual( addr_test.toString(), sData )

        self.assertEqual( type(addr_test.data), SGT.SNodePlace )
        ##################################################################################################
        sData = "OnAgent=555"
        addr = CBoxAddress( EBoxAddressType.OnAgent, data=555 )
        addr_test = CBoxAddress.fromString( sData )

        self.assertEqual( addr, addr_test )
        self.assertEqual( addr.toString(), sData )
        self.assertEqual( addr_test.toString(), sData )

if __name__ == "__main__":
    unittest.main()
