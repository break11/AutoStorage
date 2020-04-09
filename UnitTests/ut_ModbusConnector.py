#!/usr/bin/python3.7
import unittest

import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )

import Lib.Common.ModbusTypes as MT
import Lib.Common.ModbusConnector_Funcs as MCF

class Test_Modbus_Connector(unittest.TestCase):

    def test_pack_register_cache( self ):

        ###################################################################################
        reg_cache = {}
        packed_cache = []

        test_packed_cache = MCF.pack_register_cache( reg_cache )
        self.assertEqual( packed_cache, test_packed_cache )
        ###################################################################################
        reg_cache = { 0:0, 1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 8:8, 9:9 }
        packed_cache = [ MCF.regPacket( start=0, count=10, vals=[0,1,2,3,4,5,6,7,8,9] ) ]

        test_packed_cache = MCF.pack_register_cache( reg_cache )
        self.assertEqual( packed_cache, test_packed_cache )
        ###################################################################################
        reg_cache = { 9:9, 8:8, 7:7, 6:6, 5:5, 4:4, 3:3, 2:2, 1:1, 0:0 }
        packed_cache = [ MCF.regPacket( start=0, count=10, vals=[0,1,2,3,4,5,6,7,8,9] ) ]

        test_packed_cache = MCF.pack_register_cache( reg_cache )
        self.assertEqual( packed_cache, test_packed_cache )
        ###################################################################################
        reg_cache = { 5:0, 6:0, 7:0, 8:0, 9:0 }
        packed_cache = [ MCF.regPacket( start=5, count=5, vals=[0,0,0,0,0] ) ]

        test_packed_cache = MCF.pack_register_cache( reg_cache )
        self.assertEqual( packed_cache, test_packed_cache )
        ###################################################################################
        reg_cache = { 1:1, 2:2, 3:3, 5:0, 6:0, 7:0, 8:0, 9:0, 53:1, 56:80, 80:1, 0:9 }
        packed_cache = [
                            MCF.regPacket( start = 0,  count = 4, vals = [9, 1, 2, 3]    ),
                            MCF.regPacket( start = 5,  count = 5, vals = [0, 0, 0, 0, 0] ),
                            MCF.regPacket( start = 53, count = 1, vals = [1]             ),
                            MCF.regPacket( start = 56, count = 1, vals = [80]            ),
                            MCF.regPacket( start = 80, count = 1, vals = [1]             )
                        ]

        test_packed_cache = MCF.pack_register_cache( reg_cache )
        self.assertEqual( packed_cache, test_packed_cache )

if __name__ == "__main__":
    unittest.main()