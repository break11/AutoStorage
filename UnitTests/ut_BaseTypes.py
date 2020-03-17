#!/usr/bin/python3.7

import unittest

import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )

import Lib.Common.BaseTypes as BT

import Lib.GraphEntity.StorageGraphTypes as SGT
from Lib.AgentEntity.AgentServer_Event import EAgentServer_Event as EV
from Lib.AgentEntity.AgentServerPacket import CAgentServerPacket
import Lib.AgentEntity.AgentDataTypes as ADT
from Lib.AgentEntity.routeBuilder import ERouteStatus

class Test_BaseTypes(unittest.TestCase):
    def test_SIPAddress( self ):
        sData = f"127.0.0.1{ BT.SIPAddress.DS }5020"
        IPAddress = BT.SIPAddress( address = "127.0.0.1", port = 5020 )
        IPAddress_test = BT.SIPAddress.fromString( sData )

        self.assertTrue( IPAddress.bValid )
        self.assertEqual( IPAddress.bValid, IPAddress_test.bValid )
        self.assertEqual( IPAddress.address, IPAddress_test.address )
        self.assertEqual( IPAddress.port, IPAddress_test.port )

        self.assertEqual( sData, IPAddress.toString() )

        # проверка правильной обработки некорректных данных в пакете HW - символы вместо int

        sData = "fdfdfdfdfd"
        packet = CAgentServerPacket( event = EV.HelloWorld, data = ADT.SHW_Data.fromString( sData ) )

        eData = packet.data

        self.assertEqual( type(eData), ADT.SHW_Data )
        self.assertEqual( eData.agentN, "XXX" )
        self.assertEqual( eData.bIsValid, False )


if __name__ == '__main__':
    unittest.main()
