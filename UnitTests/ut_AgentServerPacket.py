import unittest

import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )

from App.AgentsManager.AgentServer_Event import EAgentServer_Event
from App.AgentsManager.AgentServerPacket import CAgentServerPacket

class TestAgentServerPacket(unittest.TestCase):

    def test_fromBStr(self):
        p1 = CAgentServerPacket( event=EAgentServer_Event.HelloWorld, packetN=0 )
        p2 = CAgentServerPacket.fromTX_BStr( b"000,000:@HW" )
        p3 = b"000,000:@HW"

        print( p1.toTX_BStr(), p2.toTX_BStr(), p3 )
        self.assertEqual( p1.toTX_BStr(), p2.toTX_BStr() )
        self.assertEqual( p1.toTX_BStr(), p3 )
        ###################################################
        p1 = CAgentServerPacket( event=EAgentServer_Event.HelloWorld, agentN=555, packetN=11, channelN=1, timeStamp=10, data="000" )
        p2 = CAgentServerPacket.fromRX_BStr( b"011,555,1,00000010:@HW:000" )
        p3 = b"011,555,1,00000010:@HW:000"

        print( p1.toRX_BStr(), p2.toRX_BStr(), p3 )
        self.assertEqual( p1.toRX_BStr(), p2.toRX_BStr() )
        self.assertEqual( p1.toRX_BStr(), p3 )
        ###################################################
        p1 = CAgentServerPacket( event=EAgentServer_Event.ClientAccepting, packetN=23 )
        p2 = CAgentServerPacket.fromRX_BStr( b"@CA:023" )
        p3 = b"@CA:023"

        print( p1.toRX_BStr(), p2.toTX_BStr(), p3 )
        self.assertEqual( p1.toRX_BStr(), p2.toTX_BStr() )
        self.assertEqual( p1.toTX_BStr(), p3 )
        ###################################################
        p1 = CAgentServerPacket( event=EAgentServer_Event.ServerAccepting, packetN=31 )
        p2 = CAgentServerPacket.fromRX_BStr( b"@SA:031" )
        p3 = b"@SA:031"

        print( p1.toRX_BStr(), p2.toTX_BStr(), p3 )
        self.assertEqual( p1.toRX_BStr(), p2.toTX_BStr() )
        self.assertEqual( p1.toTX_BStr(), p3 )
        ###################################################
        p1 = CAgentServerPacket( event=EAgentServer_Event.BatteryState, packetN=51, agentN=555 )
        p2 = CAgentServerPacket.fromTX_BStr( b"051,555:@BS" )
        p3 = b"051,555:@BS"

        print( p1.toTX_BStr(), p2.toTX_BStr(), p3 )
        self.assertEqual( p1.toTX_BStr(), p2.toTX_BStr() )
        self.assertEqual( p1.toTX_BStr(), p3 )
        ###################################################
        p1 = CAgentServerPacket( event=EAgentServer_Event.BatteryState, agentN=777, packetN=35, channelN=2, timeStamp=20, data="S,43.2V,39.31V,47.43V,-0.06A" )
        p2 = CAgentServerPacket.fromRX_BStr( b"035,777,2,00000020:@BS:S,43.2V,39.31V,47.43V,-0.06A" )
        p3 = b"035,777,2,00000020:@BS:S,43.2V,39.31V,47.43V,-0.06A"

        print( p1.toRX_BStr(), p2.toRX_BStr(), p3 )
        self.assertEqual( p1.toRX_BStr(), p2.toRX_BStr() )
        self.assertEqual( p1.toRX_BStr(), p3 )

if __name__ == '__main__':
    unittest.main()