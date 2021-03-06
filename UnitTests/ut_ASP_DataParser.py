#!/usr/bin/python3.7

import unittest

import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )

import Lib.GraphEntity.StorageGraphTypes as SGT
from Lib.AgentEntity.AgentServer_Event import EAgentServer_Event as EV
from Lib.AgentEntity.AgentServerPacket import CAgentServerPacket
import Lib.AgentEntity.AgentDataTypes as ADT
from Lib.AgentEntity.routeBuilder import ERouteStatus

class TestASP_DataParser(unittest.TestCase):
    def test_ERouteStatus(self):
        # проверка того, что каждому статусу со значением False из энама ERouteStatus соответствует статус из энама EAgent_Status
        for routeStatus in [ x for x in ERouteStatus if x is not ERouteStatus.Normal ]:
            agentStatus = ADT.EAgent_Status.fromString( routeStatus.name )
            self.assertNotEqual( agentStatus, ADT.EAgent_Status.Undefined )

    def test_HW(self):
        sData = f"cartV1{ADT.DS}555"
        packet = CAgentServerPacket( event = EV.HelloWorld, data = ADT.SHW_Data.fromString( sData ) )

        eData = packet.data
        self.assertEqual( type(eData), ADT.SHW_Data )
        self.assertEqual( eData.agentType, "cartV1" )
        self.assertEqual( eData.agentN, "555" )
        self.assertEqual( eData.bIsValid, True )

        self.assertEqual( sData, eData.toString() )

        # проверка правильной обработки некорректных данных в пакете HW - символы вместо int

        sData = "fdfdfdfdfd"
        packet = CAgentServerPacket( event = EV.HelloWorld, data = ADT.SHW_Data.fromString( sData ) )

        eData = packet.data

        self.assertEqual( type(eData), ADT.SHW_Data )
        self.assertEqual( eData.agentN, "XXX" )
        self.assertEqual( eData.bIsValid, False )

    def test_DP(self):
        sData = ADT.SDP_Data.sDefVal
        packet = CAgentServerPacket( event = EV.DistancePassed, data = ADT.SDP_Data.fromString( sData ) )

        eData = packet.data

        self.assertEqual( type(eData), ADT.SDP_Data )

    def test_BS(self):
        sData = ADT.SBS_Data.sDefVal
        packet = CAgentServerPacket( event = EV.BatteryState, data = ADT.SBS_Data.fromString( sData ) )

        eData = packet.data

        self.assertEqual( type(eData), ADT.SBS_Data )
        self.assertEqual( eData.PowerType, ADT.EAgentBattery_Type.Supercap )
        self.assertEqual( eData.S_V, 33.44 )
        self.assertEqual( eData.L_V, 40.00 )
        self.assertEqual( eData.power_U, 47.64 )
        self.assertEqual( eData.power_I1, 1.1 )
        self.assertEqual( eData.power_I2, 0.3 )

        self.assertEqual( sData, eData.toString(bShortForm=True) )

    def test_TS(self):
        sData = ADT.STS_Data.sDefVal
        packet = CAgentServerPacket( event = EV.TemperatureState, data = ADT.STS_Data.fromString( sData ) )

        eData = packet.data

        self.assertEqual( type(eData), ADT.STS_Data )
        self.assertEqual( eData.powerSource,   24 )
        self.assertEqual( eData.wheelDriver_0, 29 )
        self.assertEqual( eData.turnDriver_3 , 25 )

        self.assertEqual( sData, eData.toString() )

    def test_OD(self):
        sData="U"
        packet = CAgentServerPacket( event = EV.OdometerDistance, data = ADT.SOdometerData.fromString( sData ) )

        eData = packet.data
        self.assertEqual( type(eData), ADT.SOdometerData )
        self.assertEqual( eData.bUndefined, True )
        self.assertEqual( eData.nDistance, 0 )

        sData = f"100{ADT.DS}1{ADT.DS}2{ADT.DS}3{ADT.DS}4"
        packet = CAgentServerPacket( event = EV.OdometerDistance, data = ADT.SOdometerData.fromString( sData ) )

        eData = packet.data
        self.assertEqual( type(eData), ADT.SOdometerData )
        self.assertEqual( eData.bUndefined, False )
        self.assertEqual( eData.nDistance, 100 )

        sData="10.5"
        packet = CAgentServerPacket( event = EV.OdometerDistance, data = ADT.SOdometerData.fromString( sData ) )

        eData = packet.data
        self.assertEqual( type(eData), ADT.SOdometerData )
        self.assertEqual( eData.bUndefined, True )
        self.assertEqual( eData.nDistance, 0 )

    def test_NT(self):
        # NT^ID
        sData= EV.Idle.toStr()
        packet = CAgentServerPacket( event = EV.NewTask, data = ADT.SNT_Data.fromString( sData ) )

        eData = packet.data
        self.assertEqual( type(eData), ADT.SNT_Data )
        self.assertEqual( eData.event, EV.Idle )
        self.assertEqual( eData.data, None )

        # NT^WO
        sData= EV.WheelOrientation.toStr()
        packet = CAgentServerPacket( event = EV.NewTask, data = ADT.SNT_Data.fromString( sData ) )

        eData = packet.data
        self.assertEqual( type(eData), ADT.SNT_Data )
        self.assertEqual( eData.event, EV.WheelOrientation )
        self.assertEqual( eData.data, None )

    def test_WO(self):
        # WO^W
        sData = SGT.EWidthType.Wide.toString()
        packet = CAgentServerPacket( event = EV.WheelOrientation, data = SGT.EWidthType.fromString( sData ) )

        eData = packet.data
        self.assertEqual( type(eData), SGT.EWidthType )
        self.assertEqual( eData, SGT.EWidthType.Wide )

        # WO^W
        sData = "W"
        packet = CAgentServerPacket( event = EV.WheelOrientation, data = SGT.EWidthType.fromString( sData ) )

        eData = packet.data
        self.assertEqual( type(eData), SGT.EWidthType )
        self.assertEqual( eData, SGT.EWidthType.Wide )

        # WO^Wide
        sData = "Wide"
        packet = CAgentServerPacket( event = EV.WheelOrientation, data = SGT.EWidthType.fromString( sData ) )

        eData = packet.data
        self.assertEqual( type(eData), SGT.EWidthType )
        self.assertEqual( eData, SGT.EWidthType.Wide )

        # WO^Narrow
        sData = "Narrow"
        packet = CAgentServerPacket( event = EV.WheelOrientation, data = SGT.EWidthType.fromString( sData ) )

        eData = packet.data
        self.assertEqual( type(eData), SGT.EWidthType )
        self.assertEqual( eData, SGT.EWidthType.Narrow )

        # WO^N
        sData = "N"
        packet = CAgentServerPacket( event = EV.WheelOrientation, data = SGT.EWidthType.fromString( sData ) )

        eData = packet.data
        self.assertEqual( type(eData), SGT.EWidthType )
        self.assertEqual( eData, SGT.EWidthType.Narrow )

if __name__ == '__main__':
    unittest.main()
