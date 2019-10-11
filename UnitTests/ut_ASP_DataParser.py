#!/usr/bin/python3.7

import unittest

import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )

from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event
from Lib.AgentProtocol.AgentServerPacket import CAgentServerPacket
import Lib.AgentProtocol.AgentDataTypes as ADT

class TestASP_DataParser(unittest.TestCase):
    def test_HW(self):
        sData = "cartV1^555"
        packet = CAgentServerPacket( event = EAgentServer_Event.HelloWorld, data = ADT.SHW_Data.fromString( sData ) )

        eData = packet.data
        self.assertEqual( type(eData), ADT.SHW_Data )
        self.assertEqual( eData.agentType, "cartV1" )
        self.assertEqual( eData.agentN, 555 )
        self.assertEqual( eData.bIsValid, True )

        self.assertEqual( sData, eData.toString() )

        # проверка правильной обработки некорректных данных в пакете HW - символы вместо int

        sData = "fdfdfdfdfd"
        packet = CAgentServerPacket( event = EAgentServer_Event.HelloWorld, data = ADT.SHW_Data.fromString( sData ) )

        eData = packet.data

        self.assertEqual( type(eData), ADT.SHW_Data )
        self.assertEqual( eData.agentN, 0 )
        self.assertEqual( eData.bIsValid, False )

    def test_BS(self):
        sData = ADT.SAgent_BatteryState.sDefVal
        packet = CAgentServerPacket( event = EAgentServer_Event.BatteryState, data = ADT.SAgent_BatteryState.fromString( sData ) )

        eData = packet.data

        self.assertEqual( type(eData), ADT.SAgent_BatteryState )
        self.assertEqual( eData.PowerType, ADT.EAgentBattery_Type.Supercap )
        self.assertEqual( eData.S_V, 33.44 )
        self.assertEqual( eData.L_V, 40.00 )
        self.assertEqual( eData.power_U, 47.64 )
        self.assertEqual( eData.power_I1, 1.1 )
        self.assertEqual( eData.power_I2, 0.3 )

        self.assertEqual( sData, eData.toString() )

    def test_TS(self):
        sData = ADT.SAgent_TemperatureState.sDefVal
        packet = CAgentServerPacket( event = EAgentServer_Event.TemperatureState, data = ADT.SAgent_TemperatureState.fromString( sData ) )

        eData = packet.data

        self.assertEqual( type(eData), ADT.SAgent_TemperatureState )
        self.assertEqual( eData.t1, 24 )
        self.assertEqual( eData.t2, 29 )
        self.assertEqual( eData.t9, 25 )

        self.assertEqual( sData, eData.toString() )

    def test_OD_OP(self):
        sData="U"
        packet = CAgentServerPacket( event = EAgentServer_Event.OdometerPassed, data = ADT.SOD_OP_Data.fromString( sData ) )

        eData = packet.data
        self.assertEqual( type(eData), ADT.SOD_OP_Data )
        self.assertEqual( eData.bUndefined, True )
        self.assertEqual( eData.nDistance, 0 )

        sData="100"
        packet = CAgentServerPacket( event = EAgentServer_Event.OdometerPassed, data = ADT.SOD_OP_Data.fromString( sData ) )

        eData = packet.data
        self.assertEqual( type(eData), ADT.SOD_OP_Data )
        self.assertEqual( eData.bUndefined, False )
        self.assertEqual( eData.nDistance, 100 )

        sData="U"
        packet = CAgentServerPacket( event = EAgentServer_Event.OdometerDistance, data = ADT.SOD_OP_Data.fromString( sData ) )

        eData = packet.data
        self.assertEqual( type(eData), ADT.SOD_OP_Data )
        self.assertEqual( eData.bUndefined, True )
        self.assertEqual( eData.nDistance, 0 )

        sData="100"
        packet = CAgentServerPacket( event = EAgentServer_Event.OdometerDistance, data = ADT.SOD_OP_Data.fromString( sData ) )

        eData = packet.data
        self.assertEqual( type(eData), ADT.SOD_OP_Data )
        self.assertEqual( eData.bUndefined, False )
        self.assertEqual( eData.nDistance, 100 )

        sData="10.5"
        packet = CAgentServerPacket( event = EAgentServer_Event.OdometerDistance, data = ADT.SOD_OP_Data.fromString( sData ) )

        eData = packet.data
        self.assertEqual( type(eData), ADT.SOD_OP_Data )
        self.assertEqual( eData.bUndefined, True )
        self.assertEqual( eData.nDistance, 0 )

if __name__ == '__main__':
    unittest.main()
