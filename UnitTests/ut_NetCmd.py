#!/usr/bin/python3.7
import unittest

import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )

from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.NetObj import CNetObj
from Lib.Net.NetCmd import CNetCmd
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Common.StrTypeConverter import CStrTypeConverter

CStrTypeConverter.registerStdType( str )

CNetObj( id=121, parent=CNetObj_Manager.rootObj, props={ "Test" : "Yes" } ) # type:ignore

class Test_NetCmd(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        CStrTypeConverter.clear()

    def testNetCmd(self):
        sCMD = f"{EV.ClientConnected}{ CNetCmd.DS }{ CNetCmd.DS }{ CNetCmd.DS }{ CNetCmd.DS }"
        cmd = CNetCmd( Event = EV.ClientConnected )
        cmd1 = CNetCmd.fromString( sCMD )

        self.assertEqual( cmd.toString(), sCMD )

        self.assertEqual( cmd, cmd1 )
        self.assertEqual( cmd1.Event, EV.ClientConnected )

        #############

        sCMD = f"{EV.ObjCreated}{ CNetCmd.DS }{121}{ CNetCmd.DS }{ CNetCmd.DS }{ CNetCmd.DS }"
        cmd = CNetCmd( Event = EV.ObjCreated, Obj_UID=121 )
        cmd1 = CNetCmd.fromString( sCMD )

        self.assertEqual( cmd.toString(), sCMD )

        self.assertEqual( cmd, cmd1 )
        self.assertEqual( cmd1.Event, EV.ObjCreated )
        self.assertEqual( cmd1.Obj_UID, 121 )

        #############

        sCMD = f"{EV.ObjPropUpdated}{ CNetCmd.DS }{121}{ CNetCmd.DS }Test{ CNetCmd.DS }Yes{ CNetCmd.DS }str"
        cmd = CNetCmd( Event = EV.ObjPropUpdated, Obj_UID=121, PropName="Test", value="Yes" )
        cmd1 = CNetCmd.fromString( sCMD )

        self.assertEqual( cmd.toString(), sCMD )

        self.assertEqual( cmd, cmd1 )
        self.assertEqual( cmd1.Event, EV.ObjPropUpdated )
        self.assertEqual( cmd1.Obj_UID, 121 )

        #############

        sCMD = f"{EV.ObjPropCreated}{ CNetCmd.DS }{121}{ CNetCmd.DS }Test_New{ CNetCmd.DS }Yes{ CNetCmd.DS }str"
        cmd = CNetCmd( Event = EV.ObjPropCreated, Obj_UID=121, PropName="Test_New", value="Yes" )
        cmd1 = CNetCmd.fromString( sCMD )

        self.assertEqual( cmd.toString(), sCMD )

        self.assertEqual( cmd, cmd1 )
        self.assertEqual( cmd1.Event, EV.ObjPropCreated )
        self.assertEqual( cmd1.Obj_UID, 121 )
        self.assertEqual( type( cmd1.value ), str )

if __name__ == "__main__":
    unittest.main()