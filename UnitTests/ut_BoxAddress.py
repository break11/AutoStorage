#!/usr/bin/python3.7

import unittest
import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )

from Lib.BoxEntity.BoxAddress import CBoxAddress, EBoxAddressType
import Lib.GraphEntity.StorageGraphTypes as SGT

class Test_CBoxAddress(unittest.TestCase):

    def test(self):
        sData = "Undefined=25,Left,555"

        addr = CBoxAddress( EBoxAddressType.Undefined, nodeID = "25", placeSide = "Left", agentN = "555" )
        addr_test = CBoxAddress.fromString( sData )

        self.assertEqual( addr, addr_test )
        self.assertEqual( addr.toString(), sData )
        self.assertEqual( addr_test.toString(), sData )

        ##################################################################################################
        sData = "BoxOnNode=25,Left"
        addr = CBoxAddress( EBoxAddressType.BoxOnNode, nodeID = "25", placeSide = SGT.ESide.Left )
        addr_test = CBoxAddress.fromString( sData )

        self.assertEqual( addr, addr_test )
        self.assertEqual( addr.toString(), sData )
        self.assertEqual( addr_test.toString(), sData )

        self.assertEqual( type(addr_test.placeSide), SGT.ESide )
        ##################################################################################################
        sData = "BoxOnAgent=555"
        addr = CBoxAddress( EBoxAddressType.BoxOnAgent, agentN=555 )
        addr_test = CBoxAddress.fromString( sData )

        self.assertEqual( addr, addr_test )
        self.assertEqual( addr.toString(), sData )
        self.assertEqual( addr_test.toString(), sData )

if __name__ == "__main__":
    unittest.main()
