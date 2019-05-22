import unittest

import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )

from App.AgentsManager.AgentServer_Event import EAgentServer_Event
from App.AgentsManager.AgentServerPacket import CAgentServerPacket

class TestAgentServerPacket(unittest.TestCase):

    def test_fromBStr(self):
        # test Text Message
        p1 = CAgentServerPacket.fromRX_BStr( b"039,002,1,00026caf:Global Power Select to SUPERCAP" )
        p2 = b"039,002,1,00026caf:Global Power Select to SUPERCAP\n"

        self.assertEqual( p1.event, EAgentServer_Event.Text )
        self.assertEqual( p1.packetN, 39 )
        self.assertEqual( p1.agentN, 2 )
        self.assertEqual( p1.channelN, 1 )
        self.assertEqual( p1.timeStamp, int("26caf", 16) )
        self.assertEqual( p1.data, "Global Power Select to SUPERCAP" )

        print( p1.toRX_BStr(), p2 )
        self.assertEqual( p1.toRX_BStr(), p2 )

        # test Warning Message
        p1 = CAgentServerPacket.fromRX_BStr( b"011,003,2,00023eee:#Warning" )
        p2 = b"011,003,2,00023eee:#Warning\n"

        self.assertEqual( p1.event, EAgentServer_Event.Warning_ )
        self.assertEqual( p1.packetN, 11 )
        self.assertEqual( p1.agentN, 3 )
        self.assertEqual( p1.channelN, 2 )
        self.assertEqual( p1.timeStamp, int("23eee", 16) )
        self.assertEqual( p1.data, "#Warning" )

        print( p1.toRX_BStr(), p2 )
        self.assertEqual( p1.toRX_BStr(), p2 )

        # test Error Message
        p1 = CAgentServerPacket.fromRX_BStr( b"011,003,2,00034fff:*Error" )
        p2 = b"011,003,2,00034fff:*Error\n"

        self.assertEqual( p1.event, EAgentServer_Event.Error )
        self.assertEqual( p1.packetN, 11 )
        self.assertEqual( p1.agentN, 3 )
        self.assertEqual( p1.channelN, 2 )
        self.assertEqual( p1.timeStamp, int("34fff", 16) )
        self.assertEqual( p1.data, "*Error" )

        print( p1.toRX_BStr(), p2 )
        self.assertEqual( p1.toRX_BStr(), p2 )

        # 039,002,1,00026caf:#Warning
        # 039,002,1,00026caf:*Error

        ###################################################
        # test remove "line feed" = "\n"
        p1 = CAgentServerPacket.fromTX_BStr( b"000,000:@HW\n" )
        p2 = b"000,000:@HW\n"
        p3 = b"000,000:@HW"

        print( p1.toTX_BStr(), p2 )
        self.assertEqual( p1.toTX_BStr(), p2 )

        print( p1.toTX_BStr( appendLF=False ), p3 )
        self.assertEqual( p1.toTX_BStr( appendLF=False ), p3 )
        ###################################################
        # test return None value when can't parse string
        pNone = CAgentServerPacket.fromTX_BStr( b"Not supported cmd - 'COLON' symbol not present!" )
        print( pNone, "None" )
        self.assertEqual( pNone, None )

        pNone = CAgentServerPacket.fromTX_BStr( b"AAA,BBB:@HW" )
        print( pNone, "None" )
        self.assertEqual( pNone, None )
        # @HW
        ###################################################
        p1 = CAgentServerPacket( event=EAgentServer_Event.HelloWorld, packetN=0 )
        p2 = CAgentServerPacket.fromTX_BStr( b"000,000:@HW" )
        p3 = b"000,000:@HW\n"

        print( p1.toTX_BStr(), p2.toTX_BStr(), p3 )
        self.assertEqual( p1.toTX_BStr(), p2.toTX_BStr() )
        self.assertEqual( p1.toTX_BStr(), p3 )
        ###################
        p1 = CAgentServerPacket( event=EAgentServer_Event.HelloWorld, agentN=555, packetN=11, channelN=1, timeStamp=int("0xA", 16), data="000" )
        p2 = CAgentServerPacket.fromRX_BStr( b"011,555,1,0000000a:@HW:000" )
        p3 = b"011,555,1,0000000a:@HW:000\n"

        print( p1.toRX_BStr(), p2.toRX_BStr(), p3 )
        self.assertEqual( p1.toRX_BStr(), p2.toRX_BStr() )
        self.assertEqual( p1.toRX_BStr(), p3 )
        # @CA
        ###################################################
        p1 = CAgentServerPacket( event=EAgentServer_Event.ClientAccepting, packetN=23 )
        p2 = CAgentServerPacket.fromRX_BStr( b"@CA:023" )
        p3 = b"@CA:023\n"

        print( p1.toRX_BStr(), p2.toTX_BStr(), p3 )
        self.assertEqual( p1.toRX_BStr(), p2.toTX_BStr() )
        self.assertEqual( p1.toTX_BStr(), p3 )
        # @SA
        ###################################################
        p1 = CAgentServerPacket( event=EAgentServer_Event.ServerAccepting, packetN=31 )
        p2 = CAgentServerPacket.fromRX_BStr( b"@SA:031" )
        p3 = b"@SA:031\n"

        print( p1.toRX_BStr(), p2.toTX_BStr(), p3 )
        self.assertEqual( p1.toRX_BStr(), p2.toTX_BStr() )
        self.assertEqual( p1.toTX_BStr(), p3 )
        # @BS
        ###################################################
        p1 = CAgentServerPacket( event=EAgentServer_Event.BatteryState, packetN=51, agentN=555 )
        p2 = CAgentServerPacket.fromTX_BStr( b"051,555:@BS" )
        p3 = b"051,555:@BS\n"

        print( p1.toTX_BStr(), p2.toTX_BStr(), p3 )
        self.assertEqual( p1.toTX_BStr(), p2.toTX_BStr() )
        self.assertEqual( p1.toTX_BStr(), p3 )
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.BatteryState, agentN=777, packetN=35, channelN=2, timeStamp=int("20", 16), data="S,43.2V,39.31V,47.43V,-0.06A" )
        p2 = CAgentServerPacket.fromRX_BStr( b"035,777,2,00000020:@BS:S,43.2V,39.31V,47.43V,-0.06A" )
        p3 = b"035,777,2,00000020:@BS:S,43.2V,39.31V,47.43V,-0.06A\n"

        print( p1.toRX_BStr(), p2.toRX_BStr(), p3 )
        self.assertEqual( p1.toRX_BStr(), p2.toRX_BStr() )
        self.assertEqual( p1.toRX_BStr(), p3 )
        # @TS
        ###################################################
        p1 = CAgentServerPacket( event=EAgentServer_Event.TemperatureState, packetN=20, agentN=555 )
        p2 = CAgentServerPacket.fromTX_BStr( b"020,555:@TS" )
        p3 = b"020,555:@TS\n"

        print( p1.toTX_BStr(), p2.toTX_BStr(), p3 )
        self.assertEqual( p1.toTX_BStr(), p2.toTX_BStr() )
        self.assertEqual( p1.toTX_BStr(), p3 )
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.TemperatureState, packetN=2, agentN=2, timeStamp=int( "25fdc", 16 ), data="22,23,22,24,24,25,25,25,25" )
        p2 = CAgentServerPacket.fromRX_BStr( b"002,002,1,00025fdc:@TS:22,23,22,24,24,25,25,25,25" )
        p3 = b"002,002,1,00025fdc:@TS:22,23,22,24,24,25,25,25,25\n"

        print( p1.toRX_BStr(), p2.toRX_BStr(), p3 )
        self.assertEqual( p1.toRX_BStr(), p2.toRX_BStr() )
        self.assertEqual( p1.toRX_BStr(), p3 )
        # @TL
        ###################################################
        p1 = CAgentServerPacket( event=EAgentServer_Event.TaskList, packetN=40, agentN=22 )
        p2 = CAgentServerPacket.fromTX_BStr( b"040,022:@TL" )
        p3 = b"040,022:@TL\n"

        print( p1.toTX_BStr(), p2.toTX_BStr(), p3 )
        self.assertEqual( p1.toTX_BStr(), p2.toTX_BStr() )
        self.assertEqual( p1.toTX_BStr(), p3 )
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.TaskList, packetN=40, agentN=215, timeStamp=int( "AABB", 16 ), data="035" )
        p2 = CAgentServerPacket.fromRX_BStr( b"040,215,1,0000aabb:@TL:035" )
        p3 = b"040,215,1,0000aabb:@TL:035\n"

        print( p1.toRX_BStr(), p2.toRX_BStr(), p3 )
        self.assertEqual( p1.toRX_BStr(), p2.toRX_BStr() )
        self.assertEqual( p1.toRX_BStr(), p3 )
        # @WO
        ###################################################
        p1 = CAgentServerPacket( event=EAgentServer_Event.WheelOrientation, packetN=40, agentN=22 )
        p2 = CAgentServerPacket.fromTX_BStr( b"040,022:@WO" )
        p3 = b"040,022:@WO\n"

        print( p1.toTX_BStr(), p2.toTX_BStr(), p3 )
        self.assertEqual( p1.toTX_BStr(), p2.toTX_BStr() )
        self.assertEqual( p1.toTX_BStr(), p3 )
        # @NT
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.NewTask, packetN=40, agentN=215, timeStamp=int( "AABB", 16 ), data="DP" )
        p2 = CAgentServerPacket.fromRX_BStr( b"040,215,1,0000aabb:@NT:DP" )
        p3 = b"040,215,1,0000aabb:@NT:DP\n"

        print( p1.toRX_BStr(), p2.toRX_BStr(), p3 )
        self.assertEqual( p1.toRX_BStr(), p2.toRX_BStr() )
        self.assertEqual( p1.toRX_BStr(), p3 )
        # @PE
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.PowerOn, packetN=20, agentN=31 )
        p2 = CAgentServerPacket.fromTX_Str( "020,031:@PE" )
        p3 = b"020,031:@PE\n"

        print( p1.toTX_BStr(), p2.toTX_BStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.PowerOn )
        self.assertEqual( p1.toTX_BStr(), p2.toTX_BStr() )
        self.assertEqual( p1.toTX_BStr(), p3 )
        # @PD
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.PowerOff, packetN=444, agentN=222 )
        p2 = CAgentServerPacket.fromTX_Str( "444,222:@PD" )
        p3 = b"444,222:@PD\n"

        print( p1.toTX_BStr(), p2.toTX_BStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.PowerOff )
        self.assertEqual( p1.toTX_BStr(), p2.toTX_BStr() )
        self.assertEqual( p1.toTX_BStr(), p3 )
        # @BR
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.BrakeRelease, packetN=111, agentN=333 )
        p2 = CAgentServerPacket.fromTX_Str( "111,333:@BR" )
        p3 = b"111,333:@BR\n"

        print( p1.toTX_BStr(), p2.toTX_BStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.BrakeRelease )
        self.assertEqual( p1.toTX_BStr(), p2.toTX_BStr() )
        self.assertEqual( p1.toTX_BStr(), p3 )
        # @ES
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.EmergencyStop, packetN=777, agentN=888 )
        p2 = CAgentServerPacket.fromTX_Str( "777,888:@ES" )
        p3 = b"777,888:@ES\n"

        print( p1.toTX_BStr(), p2.toTX_BStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.EmergencyStop )
        self.assertEqual( p1.toTX_BStr(), p2.toTX_BStr() )
        self.assertEqual( p1.toTX_BStr(), p3 )
        # @SB
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.SequenceBegin, packetN=1, agentN=1 )
        p2 = CAgentServerPacket.fromTX_Str( "001,001:@SB" )
        p3 = b"001,001:@SB\n"

        print( p1.toTX_BStr(), p2.toTX_BStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.SequenceBegin )
        self.assertEqual( p1.toTX_BStr(), p2.toTX_BStr() )
        self.assertEqual( p1.toTX_BStr(), p3 )
        # @SE
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.SequenceEnd, packetN=999, agentN=10 )
        p2 = CAgentServerPacket.fromTX_Str( "999,010:@SE" )
        p3 = b"999,010:@SE\n"

        print( p1.toTX_BStr(), p2.toTX_BStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.SequenceEnd )
        self.assertEqual( p1.toTX_BStr(), p2.toTX_BStr() )
        self.assertEqual( p1.toTX_BStr(), p3 )
        # @DP
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.DistancePassed, packetN=1, agentN=11, data="000331,F,H,B,C" )
        p2 = CAgentServerPacket.fromTX_Str( "001,011:@DP:000331,F,H,B,C" )
        p3 = b"001,011:@DP:000331,F,H,B,C\n"

        print( p1.toTX_BStr(), p2.toTX_BStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.DistancePassed )
        self.assertEqual( p1.toTX_BStr(), p2.toTX_BStr() )
        self.assertEqual( p1.toTX_BStr(), p3 )
        # @OZ
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.OdometerZero, packetN=272, agentN=2, channelN=2, timeStamp=int("2a7f0", 16) )
        p2 = CAgentServerPacket.fromRX_Str( "272,002,2,0002a7f0:@OZ" )
        p3 = b"272,002,2,0002a7f0:@OZ\n"

        print( p1.toRX_BStr(), p2.toRX_BStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.OdometerZero )
        self.assertEqual( p1.toRX_BStr(), p2.toRX_BStr() )
        self.assertEqual( p1.toRX_BStr(), p3 )
        # @OP
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.OdometerPassed, packetN=40, agentN=215, timeStamp=int( "AABB", 16 ), data="50" )
        p2 = CAgentServerPacket.fromRX_BStr( b"040,215,1,0000aabb:@OP:50" )
        p3 = b"040,215,1,0000aabb:@OP:50\n"

        print( p1.toRX_BStr(), p2.toRX_BStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.OdometerPassed )
        self.assertEqual( p1.toRX_BStr(), p2.toRX_BStr() )
        self.assertEqual( p1.toRX_BStr(), p3 )
        # @OD
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.OdometerDistance, packetN=40, agentN=215, timeStamp=int( "AABB", 16 ), data="50" )
        p2 = CAgentServerPacket.fromRX_BStr( b"040,215,1,0000aabb:@OD:50" )
        p3 = b"040,215,1,0000aabb:@OD:50\n"

        print( p1.toRX_BStr(), p2.toRX_BStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.OdometerDistance )
        self.assertEqual( p1.toRX_BStr(), p2.toRX_BStr() )
        self.assertEqual( p1.toRX_BStr(), p3 )

if __name__ == '__main__':
    unittest.main()