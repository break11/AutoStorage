#!/usr/bin/python3.7

import unittest

import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )

from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event
from Lib.AgentProtocol.AgentServerPacket import CAgentServerPacket, MS, DS

class TestAgentServerPacket(unittest.TestCase):

    def test_fromStr_toStr(self):
        # test Error Message with multiple symbol ":"
        s = f"039{MS}002{MS}00026caf{MS}@ER{MS}*111:222:333"
        p1 = CAgentServerPacket.fromStr( s )
        p2 = s + "\n"

        self.assertEqual( p1.event, EAgentServer_Event.Error )
        self.assertEqual( p1.packetN, 39 )
        self.assertEqual( p1.agentN, 2 )
        self.assertEqual( p1.timeStamp, int("26caf", 16) )
        self.assertEqual( p1.data, "*111:222:333" )

        print( p1.toStr(), p2 )
        self.assertEqual( p1.toStr(), p2 )

        p1 = CAgentServerPacket.fromStr( "039,002,1,00026caf:@ER:111:222:333" )
        p2 = "039,002,1,00026caf:@ER:111:222:333\n"

        print( p1.toStr(), p2 )
        self.assertEqual( p1.toStr(), p2 )

        p1 = CAgentServerPacket.fromStr( "039,002,1,00026caf:@ER:111:222:333:" )
        p2 = "039,002,1,00026caf:@ER:111:222:333:\n"

        self.assertEqual( p1.event, EAgentServer_Event.Error )
        print( p1.toStr(), p2 )
        self.assertEqual( p1.toStr(), p2 )
        ###############################################

        # test Text Message
        p1 = CAgentServerPacket.fromStr( "039,002,1,00026caf:@TX:Global Power Select to SUPERCAP" )
        p2 = "039,002,1,00026caf:@TX:Global Power Select to SUPERCAP\n"

        self.assertEqual( p1.event, EAgentServer_Event.Text )
        self.assertEqual( p1.packetN, 39 )
        self.assertEqual( p1.agentN, 2 )
        self.assertEqual( p1.channelN, 1 )
        self.assertEqual( p1.timeStamp, int("26caf", 16) )
        self.assertEqual( p1.data, "Global Power Select to SUPERCAP" )

        print( p1.toStr(), p2 )
        self.assertEqual( p1.toStr(), p2 )

        # test Warning Message
        p1 = CAgentServerPacket.fromStr( "011,003,2,00023eee:@WR:#Warning" )
        p2 = "011,003,2,00023eee:@WR:#Warning\n"

        self.assertEqual( p1.event, EAgentServer_Event.Warning_ )
        self.assertEqual( p1.packetN, 11 )
        self.assertEqual( p1.agentN, 3 )
        self.assertEqual( p1.channelN, 2 )
        self.assertEqual( p1.timeStamp, int("23eee", 16) )
        self.assertEqual( p1.data, "#Warning" )

        print( p1.toStr(), p2 )
        self.assertEqual( p1.toStr(), p2 )

        # test Error Message
        p1 = CAgentServerPacket.fromStr( "011,003,2,00034fff:@ER:*Error" )
        p2 = "011,003,2,00034fff:@ER:*Error\n"

        self.assertEqual( p1.event, EAgentServer_Event.Error )
        self.assertEqual( p1.packetN, 11 )
        self.assertEqual( p1.agentN, 3 )
        self.assertEqual( p1.channelN, 2 )
        self.assertEqual( p1.timeStamp, int("34fff", 16) )
        self.assertEqual( p1.data, "*Error" )

        print( p1.toStr(), p2 )
        self.assertEqual( p1.toStr(), p2 )

        ###################################################
        # test remove "line feed" = "\n"
        p1 = CAgentServerPacket.fromStr( "000,000:@HW\n" )
        p2 = "000,000:@HW\n"
        p3 = "000,000:@HW"

        print( p1.toStr(), p2 )
        self.assertEqual( p1.toStr(), p2 )

        print( p1.toStr( appendLF=False ), p3 )
        self.assertEqual( p1.toStr( appendLF=False ), p3 )
        ###################################################
        # test space instead zero
        p1 = CAgentServerPacket( event=EAgentServer_Event.HelloWorld, agentN=55, packetN=11, channelN=1, timeStamp=int("0xA", 16), data="017" )
        p2 = CAgentServerPacket.fromStr( " 11, 55,1,0000000a:@HW: 17" )

        print( "int(data)=", int(p1.data), int(p2.data) )
        self.assertEqual( int(p1.data), int(p2.data) )
        print( "agentN=", p1.agentN, p2.agentN )
        self.assertEqual( p1.agentN, p2.agentN )
        print( "packetN=", p1.packetN, p2.packetN )
        self.assertEqual( p1.packetN, p2.packetN )
        ###################################################
        # test return None value when can't parse string
        pNone = CAgentServerPacket.fromStr( "Not supported cmd - 'COLON' symbol not present!" )
        print( pNone, "None" )
        self.assertEqual( pNone, None )

        pNone = CAgentServerPacket.fromStr( "AAA,BBB:@HW" )
        print( pNone, "None" )
        self.assertEqual( pNone, None )
        # @HW
        ###################################################
        p1 = CAgentServerPacket( event=EAgentServer_Event.HelloWorld, packetN=0 )
        p2 = CAgentServerPacket.fromStr( "000,000:@HW" )
        p3 = "000,000:@HW\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        ###################
        p1 = CAgentServerPacket( event=EAgentServer_Event.HelloWorld, agentN=555, packetN=11, channelN=1, timeStamp=int("0xA", 16), data="000" )
        p2 = CAgentServerPacket.fromStr( "011,555,1,0000000a:@HW:000" )
        p3 = "011,555,1,0000000a:@HW:000\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @AC
        ###################################################
        p1 = CAgentServerPacket( event=EAgentServer_Event.Accepted, packetN=23 )
        p2 = CAgentServerPacket.fromStr( "023:@AC" )
        p3 = "023:@AC\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @BS
        ###################################################
        p1 = CAgentServerPacket( event=EAgentServer_Event.BatteryState, packetN=51, agentN=555 )
        p2 = CAgentServerPacket.fromStr( "051,555:@BS" )
        p3 = "051,555:@BS\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.BatteryState, agentN=777, packetN=35, channelN=2, timeStamp=int("20", 16), data="S,43.2V,39.31V,47.43V,-0.06A" )
        p2 = CAgentServerPacket.fromStr( "035,777,2,00000020:@BS:S,43.2V,39.31V,47.43V,-0.06A" )
        p3 = "035,777,2,00000020:@BS:S,43.2V,39.31V,47.43V,-0.06A\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @TS
        ###################################################
        p1 = CAgentServerPacket( event=EAgentServer_Event.TemperatureState, packetN=20, agentN=555 )
        p2 = CAgentServerPacket.fromStr( "020,555:@TS" )
        p3 = "020,555:@TS\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.TemperatureState, packetN=2, agentN=2, timeStamp=int( "25fdc", 16 ), data="22,23,22,24,24,25,25,25,25" )
        p2 = CAgentServerPacket.fromStr( "002,002,1,00025fdc:@TS:22,23,22,24,24,25,25,25,25" )
        p3 = "002,002,1,00025fdc:@TS:22,23,22,24,24,25,25,25,25\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @TL
        ###################################################
        p1 = CAgentServerPacket( event=EAgentServer_Event.TaskList, packetN=40, agentN=22 )
        p2 = CAgentServerPacket.fromStr( "040,022:@TL" )
        p3 = "040,022:@TL\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.TaskList, packetN=40, agentN=215, timeStamp=int( "AAB", 16 ), data="035" )
        p2 = CAgentServerPacket.fromStr( "040,215,1,0000aabb:@TL:035" )
        p3 = "040,215,1,0000aabb:@TL:035\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @WO
        ###################################################
        p1 = CAgentServerPacket( event=EAgentServer_Event.WheelOrientation, packetN=40, agentN=22 )
        p2 = CAgentServerPacket.fromStr( "040,022:@WO" )
        p3 = "040,022:@WO\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @NT
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.NewTask, packetN=40, agentN=215, timeStamp=int( "AAB", 16 ), data="DP" )
        p2 = CAgentServerPacket.fromStr( "040,215,1,0000aabb:@NT:DP" )
        p3 = "040,215,1,0000aabb:@NT:DP\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @PE
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.PowerEnable, packetN=20, agentN=31 )
        p2 = CAgentServerPacket.fromStr( "020,031:@PE" )
        p3 = "020,031:@PE\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.PowerEnable )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @PD
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.PowerDisable, packetN=444, agentN=222 )
        p2 = CAgentServerPacket.fromStr( "444,222:@PD" )
        p3 = "444,222:@PD\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.PowerDisable )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @BR
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.BrakeRelease, packetN=111, agentN=333 )
        p2 = CAgentServerPacket.fromStr( "111,333:@BR" )
        p3 = "111,333:@BR\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.BrakeRelease )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @ES
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.EmergencyStop, packetN=777, agentN=888 )
        p2 = CAgentServerPacket.fromStr( "777,888:@ES" )
        p3 = "777,888:@ES\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.EmergencyStop )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @SB
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.SequenceBegin, packetN=1, agentN=1 )
        p2 = CAgentServerPacket.fromStr( "001,001:@S" )
        p3 = "001,001:@SB\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.SequenceBegin )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @SE
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.SequenceEnd, packetN=999, agentN=10 )
        p2 = CAgentServerPacket.fromStr( "999,010:@SE" )
        p3 = "999,010:@SE\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.SequenceEnd )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @DP
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.DistancePassed, packetN=1, agentN=11, data="000331,F,H,B,C" )
        p2 = CAgentServerPacket.fromStr( "001,011:@DP:000331,F,H,B,C" )
        p3 = "001,011:@DP:000331,F,H,B,C\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.DistancePassed )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @OZ
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.OdometerZero, packetN=272, agentN=2, channelN=2, timeStamp=int("2a7f0", 16) )
        p2 = CAgentServerPacket.fromStr( "272,002,2,0002a7f0:@OZ" )
        p3 = "272,002,2,0002a7f0:@OZ\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.OdometerZero )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @OP
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.OdometerPassed, packetN=40, agentN=215, timeStamp=int( "AAB", 16 ), data="50" )
        p2 = CAgentServerPacket.fromStr( "040,215,1,0000aabb:@OP:50" )
        p3 = "040,215,1,0000aabb:@OP:50\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.OdometerPassed )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @OD
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.OdometerDistance, packetN=40, agentN=215, timeStamp=int( "AAB", 16 ), data="50" )
        p2 = CAgentServerPacket.fromStr( "040,215,1,0000aabb:@OD:50" )
        p3 = "040,215,1,0000aabb:@OD:50\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.OdometerDistance )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @DE
        #########################
        p1 = CAgentServerPacket( event=EAgentServer_Event.DistanceEnd, packetN=272, agentN=2, channelN=2, timeStamp=int("2a7f0", 16) )
        p2 = CAgentServerPacket.fromStr( "272,002,2,0002a7f0:@DE" )
        p3 = "272,002,2,0002a7f0:@DE\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.DistanceEnd )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )

if __name__ == '__main__':
    unittest.main()
