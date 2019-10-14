#!/usr/bin/python3.7

import unittest

import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )

from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event
from Lib.AgentProtocol.AgentDataTypes import MS, DS
import Lib.AgentProtocol.AgentDataTypes as ADT
from Lib.AgentProtocol.AgentServerPacket import CAgentServerPacket

class TestAgentServerPacket(unittest.TestCase):

    def test_fromStr_toStr(self):
        # test Error Message with multiple symbol ":"
        s = f"039{MS}00026caf{MS}ER{MS}*111:222:333"
        p1 = CAgentServerPacket.fromStr( s )
        p2 = s + "\n"

        self.assertEqual( p1.event, EAgentServer_Event.Error )
        self.assertEqual( p1.packetN, 39 )
        self.assertEqual( p1.timeStamp, int("26caf", 16) )
        self.assertEqual( p1.data, "*111:222:333" )

        print( p1.toStr(), p2 )
        self.assertEqual( p1.toStr(), p2 )

        s = f"039{MS}00026caf{MS}ER{MS}111:222:333"
        p1 = CAgentServerPacket.fromStr( s )
        p2 = s + "\n"

        print( p1.toStr(), p2 )
        self.assertEqual( p1.toStr(), p2 )
        ###############################################

        # test Text Message
        s = f"039{MS}00026caf{MS}TX{MS}Global Power Select to SUPERCAP"
        p1 = CAgentServerPacket.fromStr( s )
        p2 = s + "\n"

        self.assertEqual( p1.event, EAgentServer_Event.Text )
        self.assertEqual( p1.packetN, 39 )
        self.assertEqual( p1.timeStamp, int("26caf", 16) )
        self.assertEqual( p1.data, "Global Power Select to SUPERCAP" )

        print( p1.toStr(), p2 )
        self.assertEqual( p1.toStr(), p2 )

        # test Warning Message
        s = f"011{MS}00023eee{MS}WR{MS}#Warning"
        p1 = CAgentServerPacket.fromStr( s )
        p2 = s + "\n"

        self.assertEqual( p1.event, EAgentServer_Event.Warning_ )
        self.assertEqual( p1.packetN, 11 )
        self.assertEqual( p1.timeStamp, int("23eee", 16) )
        self.assertEqual( p1.data, "#Warning" )

        print( p1.toStr(), p2 )
        self.assertEqual( p1.toStr(), p2 )

        # test Error Message
        s = f"011{MS}00034fff{MS}ER{MS}*Error"
        p1 = CAgentServerPacket.fromStr( s )
        p2 = s + "\n"

        self.assertEqual( p1.event, EAgentServer_Event.Error )
        self.assertEqual( p1.packetN, 11 )
        self.assertEqual( p1.timeStamp, int("34fff", 16) )
        self.assertEqual( p1.data, "*Error" )

        print( p1.toStr(), p2 )
        self.assertEqual( p1.toStr(), p2 )

        ###################################################
        # test remove "line feed" = "\n"
        s = f"000{MS}{MS}HW{MS}\n"
        p1 = CAgentServerPacket.fromStr( s )
        p2 = s
        p3 = f"000{MS}{MS}HW{MS}"

        print( p1.toStr(), p2 )
        self.assertEqual( p1.toStr(), p2 )

        print( p1.toStr( appendLF=False ), p3 )
        self.assertEqual( p1.toStr( appendLF=False ), p3 )
        ###################################################
        # test space instead zero
        p1 = CAgentServerPacket( event=EAgentServer_Event.HelloWorld, packetN=11, timeStamp=int("0xA", 16), data=ADT.SHW_Data.fromString( f"cartV1{DS}17" ) )
        p2 = CAgentServerPacket.fromStr( f" 11{MS} 0000000a{MS}HW{MS}cartV1{DS}17" )

        print( "int(data)=", p1.data, p2.data )
        self.assertEqual( str(p1.data), str(p2.data) )
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
        s = f"000{MS}{MS}HW{MS}"
        p1 = CAgentServerPacket( event=EAgentServer_Event.HelloWorld, packetN=0 )
        p2 = CAgentServerPacket.fromStr( s )
        p3 = s + "\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        ###################
        s = f"011{MS}0000000a{MS}HW{MS}"
        p1 = CAgentServerPacket( event=EAgentServer_Event.HelloWorld, packetN=11, timeStamp=int("0xA", 16) )
        p2 = CAgentServerPacket.fromStr( s )
        p3 = s + "\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @AC
        ###################################################
        s = f"023{MS}{MS}AC{MS}"
        p1 = CAgentServerPacket( event=EAgentServer_Event.Accepted, packetN=23 )
        p2 = CAgentServerPacket.fromStr( s )
        p3 = s + "\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @BS
        ###################################################
        s = f"051{MS}{MS}BS{MS}"
        p1 = CAgentServerPacket( event=EAgentServer_Event.BatteryState, packetN=51 )
        p2 = CAgentServerPacket.fromStr( s )
        p3 = s + "\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        #########################
        sData = f"S{DS}43.20V{DS}39.31V{DS}47.43V{DS}1.10A{DS}-0.06A"
        s = f"035{MS}00000020{MS}BS{MS}{sData}"
        p1 = CAgentServerPacket( event=EAgentServer_Event.BatteryState, packetN=35, timeStamp=int("20", 16), data=ADT.SAgent_BatteryState.fromString( sData ) )
        p2 = CAgentServerPacket.fromStr( s )
        p3 = s + "\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @TS
        ###################################################
        s = f"020{MS}{MS}TS{MS}"
        p1 = CAgentServerPacket( event=EAgentServer_Event.TemperatureState, packetN=20 )
        p2 = CAgentServerPacket.fromStr( s )
        p3 = s + "\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        #########################
        sData = f"22{DS}23{DS}22{DS}24{DS}24{DS}25{DS}25{DS}25{DS}25"
        s = f"002{MS}00025fdc{MS}TS{MS}{sData}"
        p1 = CAgentServerPacket( event=EAgentServer_Event.TemperatureState, packetN=2, timeStamp=int( "25fdc", 16 ), data=ADT.SAgent_TemperatureState.fromString( sData ) )
        p2 = CAgentServerPacket.fromStr( s )
        p3 = s + "\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @TL
        ###################################################
        s = f"040{MS}{MS}TL{MS}"
        p1 = CAgentServerPacket( event=EAgentServer_Event.TaskList, packetN=40 )
        p2 = CAgentServerPacket.fromStr( s )
        p3 = s + "\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        #########################
        sData = "035"
        s = f"040{MS}00000aab{MS}TL{MS}{sData}"
        p1 = CAgentServerPacket( event=EAgentServer_Event.TaskList, packetN=40, timeStamp=int( "AAB", 16 ), data=sData )
        p2 = CAgentServerPacket.fromStr( s )
        p3 = s + "\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @WO
        ###################################################
        s = f"040{MS}{MS}WO{MS}"
        p1 = CAgentServerPacket( event=EAgentServer_Event.WheelOrientation, packetN=40 )
        p2 = CAgentServerPacket.fromStr( s )
        p3 = s + "\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @NT
        #########################
        sData = "DP"
        s = f"040{MS}0000aabb{MS}NT{MS}{sData}"
        p1 = CAgentServerPacket( event=EAgentServer_Event.NewTask, packetN=40, timeStamp=int( "AABB", 16 ), data=ADT.SNT_Data.fromString( sData ) )
        p2 = CAgentServerPacket.fromStr( s )
        p3 = s + "\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @PE
        #########################
        s = f"020{MS}{MS}PE{MS}"
        p1 = CAgentServerPacket( event=EAgentServer_Event.PowerEnable, packetN=20 )
        p2 = CAgentServerPacket.fromStr( s )
        p3 = s + "\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.PowerEnable )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @PD
        #########################
        s = f"444{MS}{MS}PD{MS}"
        p1 = CAgentServerPacket( event=EAgentServer_Event.PowerDisable, packetN=444 )
        p2 = CAgentServerPacket.fromStr( s )
        p3 = s + "\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.PowerDisable )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @BR
        #########################
        s = f"111{MS}{MS}BR{MS}"
        p1 = CAgentServerPacket( event=EAgentServer_Event.BrakeRelease, packetN=111 )
        p2 = CAgentServerPacket.fromStr( s )
        p3 = s + "\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.BrakeRelease )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @ES
        #########################
        s = f"777{MS}{MS}ES{MS}"
        p1 = CAgentServerPacket( event=EAgentServer_Event.EmergencyStop, packetN=777 )
        p2 = CAgentServerPacket.fromStr( s )
        p3 = s + "\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.EmergencyStop )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @SB
        #########################
        s = f"001{MS}{MS}SB{MS}"
        p1 = CAgentServerPacket( event=EAgentServer_Event.SequenceBegin, packetN=1)
        p2 = CAgentServerPacket.fromStr( s )
        p3 = s + "\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.SequenceBegin )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @SE
        #########################
        s = f"999{MS}{MS}SE{MS}"
        p1 = CAgentServerPacket( event=EAgentServer_Event.SequenceEnd, packetN=999)
        p2 = CAgentServerPacket.fromStr( s )
        p3 = s + "\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.SequenceEnd )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @DP
        #########################
        sData = "000331,F,H,B,C"
        s = f"001{MS}{MS}DP{MS}{sData}"
        p1 = CAgentServerPacket( event=EAgentServer_Event.DistancePassed, packetN=1, data=sData )
        p2 = CAgentServerPacket.fromStr( s )
        p3 = s + "\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.DistancePassed )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @OZ
        #########################
        s = f"272{MS}0002a7f0{MS}OZ{MS}"
        p1 = CAgentServerPacket( event=EAgentServer_Event.OdometerZero, packetN=272, timeStamp=int("2a7f0", 16) )
        p2 = CAgentServerPacket.fromStr( s )
        p3 = s + "\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.OdometerZero )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @OP
        #########################
        sData = "50"
        s = f"040{MS}0000aabb{MS}OP{MS}{sData}"
        p1 = CAgentServerPacket( event=EAgentServer_Event.OdometerPassed, packetN=40, timeStamp=int( "AABB", 16 ), data=ADT.SOD_OP_Data.fromString( sData ) )
        p2 = CAgentServerPacket.fromStr( s )
        p3 = s + "\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.OdometerPassed )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @OD
        #########################
        sData = "50"
        s = f"040{MS}0000aabb{MS}OD{MS}{sData}"
        p1 = CAgentServerPacket( event=EAgentServer_Event.OdometerDistance, packetN=40, timeStamp=int( "AABB", 16 ), data=ADT.SOD_OP_Data.fromString( sData ) )
        p2 = CAgentServerPacket.fromStr( s )
        p3 = s + "\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.OdometerDistance )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )
        # @DE
        #########################
        s = f"272{MS}0002a7f0{MS}DE{MS}"
        p1 = CAgentServerPacket( event=EAgentServer_Event.DistanceEnd, packetN=272, timeStamp=int("2a7f0", 16) )
        p2 = CAgentServerPacket.fromStr( s )
        p3 = s + "\n"

        print( p1.toStr(), p2.toStr(), p3 )
        self.assertEqual( p2.event, EAgentServer_Event.DistanceEnd )
        self.assertEqual( p1.toStr(), p2.toStr() )
        self.assertEqual( p1.toStr(), p3 )

if __name__ == '__main__':
    unittest.main()
