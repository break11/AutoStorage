#!/usr/bin/python3.7

import unittest

import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )

from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event
from Lib.AgentProtocol.AgentServerPacket import CAgentServerPacket
from Lib.AgentProtocol.ASP_DataParser import extractASP_Data
from Lib.AgentProtocol.AgentDataTypes import SAgent_BatteryState, EAgentBattery_Type, SFakeAgent_DevPacketData, SOD_OP_Data

class TestASP_DataParser(unittest.TestCase):
    def test_BS(self):
        sData = "S,33.44V,40.00V,47.64V,01.1A/00.3A"
        packet = CAgentServerPacket( event = EAgentServer_Event.BatteryState, data = sData )

        eData = extractASP_Data( packet )

        self.assertEqual( type(eData), SAgent_BatteryState )
        self.assertEqual( eData.PowerType, EAgentBattery_Type.Supercap )
        self.assertEqual( eData.S_V, 33.44 )
        self.assertEqual( eData.L_V, 40.00 )
        self.assertEqual( eData.power_U, 47.64 )
        self.assertEqual( eData.power_I1, 1.1 )
        self.assertEqual( eData.power_I2, 0.3 )

        self.assertEqual( sData, eData.toString() )

    def test_FA(self):
        sData = f"1"
        packet = CAgentServerPacket( event = EAgentServer_Event.FakeAgentDevPacket, data = sData )

        eData = extractASP_Data( packet )
        self.assertEqual( type(eData), SFakeAgent_DevPacketData )
        self.assertEqual( eData.bCharging, True )

        self.assertEqual( sData, eData.toString() )

        sData = f"0"
        packet = CAgentServerPacket( event = EAgentServer_Event.FakeAgentDevPacket, data = sData )
        eData = extractASP_Data( packet )
        self.assertEqual( type(eData), SFakeAgent_DevPacketData )
        self.assertEqual( eData.bCharging, False )

        self.assertEqual( sData, eData.toString() )

    def test_OD_OP(self):
        sData="U"
        packet = CAgentServerPacket( event = EAgentServer_Event.OdometerPassed, data = sData )

        eData = extractASP_Data( packet )
        self.assertEqual( type(eData), SOD_OP_Data )
        self.assertEqual( eData.bUndefined, True )
        self.assertEqual( eData.nDistance, 0 )

        sData="100"
        packet = CAgentServerPacket( event = EAgentServer_Event.OdometerPassed, data = sData )

        eData = extractASP_Data( packet )
        self.assertEqual( type(eData), SOD_OP_Data )
        self.assertEqual( eData.bUndefined, False )
        self.assertEqual( eData.nDistance, 100 )

        sData="U"
        packet = CAgentServerPacket( event = EAgentServer_Event.OdometerDistance, data = sData )

        eData = extractASP_Data( packet )
        self.assertEqual( type(eData), SOD_OP_Data )
        self.assertEqual( eData.bUndefined, True )
        self.assertEqual( eData.nDistance, 0 )

        sData="100"
        packet = CAgentServerPacket( event = EAgentServer_Event.OdometerDistance, data = sData )

        eData = extractASP_Data( packet )
        self.assertEqual( type(eData), SOD_OP_Data )
        self.assertEqual( eData.bUndefined, False )
        self.assertEqual( eData.nDistance, 100 )

        sData="10.5"
        packet = CAgentServerPacket( event = EAgentServer_Event.OdometerDistance, data = sData )

        eData = extractASP_Data( packet )
        self.assertEqual( type(eData), SOD_OP_Data )
        self.assertEqual( eData.bUndefined, True )
        self.assertEqual( eData.nDistance, 0 )

if __name__ == '__main__':
    unittest.main()
