#!/usr/bin/python3.7

import unittest

import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )

from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event
from Lib.AgentProtocol.AgentServerPacket import CAgentServerPacket
from Lib.AgentProtocol.ASP_DataParser import extractASP_Data, SAgent_BatteryState, EAgentBattery_Type

class TestASP_DataParser(unittest.TestCase):
    def test_exstractBS(self):
        packet = CAgentServerPacket( event = EAgentServer_Event.BatteryState, data = "S,33.44V,40.00V,47.64V,01.1A/00.3A" )

        eData = extractASP_Data( packet )

        self.assertEqual( type(eData), SAgent_BatteryState )
        self.assertEqual( eData.PowerType, EAgentBattery_Type.Supercap )
        self.assertEqual( eData.S_V, 33.44 )
        self.assertEqual( eData.L_V, 40.00 )
        self.assertEqual( eData.power_U, 47.64 )
        self.assertEqual( eData.power_I1, 1.1 )
        self.assertEqual( eData.power_I2, 0.3 )

        print( eData.toString() )

if __name__ == '__main__':
    unittest.main()
