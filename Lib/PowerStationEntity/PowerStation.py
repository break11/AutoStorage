import weakref
from collections import namedtuple
from PyQt5.QtNetwork import QTcpSocket, QAbstractSocket

from Lib.Common.StrConsts import SC
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Common.TickManager import CTickManager
from Lib.Net.NetObj_Utils import isSelfEvent
import Lib.PowerStationEntity.PowerStationTypes as PST
import Lib.GraphEntity.StorageGraphTypes as SGT
import Lib.Common.BaseTypes as BT

import Lib.PowerStationEntity.ChargeUtils as CU

ECS = PST.EChargeStage
EPS = PST.EChargeState
PSC = PST.PowerStationCommands

PowerDesc = namedtuple( "PowerDesc", "data stage", defaults = (None, None) )

class CUSB_PowerHandler:
    def mainTick(self): pass

    def setPowerState(self, powerState):
        CU.controlCharge( powerState, self.address_data )

    # def __del__(self):
    #     CU.controlCharge( EPS.off, self.address_data )

class CTCP_IP_PowerHandler:

    PD_Funcs_byChargeStage = {
        # Получить статус удаленного управления
        ECS.GetState    : lambda obj : PowerDesc( data = PSC.GetState ),
        # Переключить на удаленное управление
        ECS.SetRemote   : lambda obj : PowerDesc( data = PSC.SetRemote, stage = ECS.SetReset ),
        # Выполнить сброс устройства для переключения в режим удаленного управления
        ECS.SetReset    : lambda obj : PowerDesc( data = PSC.SetReset, stage = ECS.GetState ),
        # Отправить запрос на получение напряжения
        ECS.GetVoltage  : lambda obj : PowerDesc( data = PSC.GetVoltage ),
        # Отправить запрос на получение тока
        ECS.GetCurrent  : lambda obj : PowerDesc( data = PSC.GetCurrent ),
        # Отключить выход
        ECS.SetPowerOff : lambda obj : PowerDesc( data = PSC.SetPowerOff, stage = ECS.GetVoltage ),
        # Установить напряжение на выходе
        ECS.SetVoltage  : lambda obj : PowerDesc( data = PSC.Voltage( obj.voltageMax ), stage = ECS.SetCurrent ),
        # Установить ток на выходе
        ECS.SetCurrent  : lambda obj : PowerDesc( data = PSC.Current( obj.currentMax ), stage = ECS.SetPowerOn ),
        # Включить выход
        ECS.SetPowerOn  : lambda obj : PowerDesc( data = PSC.SetPowerOn, stage = ECS.GetVoltage ),
    }

    def __init__(self):
        self.tcpSocket = QTcpSocket()
        self.tcpSocket.readyRead.connect( self.bytesAvailable )

        self.voltageMax = 41.5
        self.currentMax = 100.0

        self.voltageFact = 0
        self.currentFact = 0

    def __del__(self):
    #     stage = self.netObj().chargeStage
    #     if stage == ECS.GetVoltage or stage == ECS.GetCurrent:
    #         self.tcpSocket.write( PSC.SetPowerOff.encode() )
        self.tcpSocket.disconnect()
    
    def mainTick(self):
        if self.tcpSocket.state() == QAbstractSocket.UnconnectedState:
            self.tcpSocket.connectToHost( self.address_data.address, self.address_data.port )

            if self.tcpSocket.waitForConnected(100):
                self.netObj().chargeStage = ECS.GetState
        
        elif self.tcpSocket.state() == QAbstractSocket.ConnectedState:
            current_stage = self.netObj().chargeStage
            func = self.PD_Funcs_byChargeStage.get( current_stage )
            targetDesc = func( self )

            if targetDesc.data is not None:
                self.tcpSocket.write( targetDesc.data.encode() )
            if targetDesc.stage is not None:
                self.netObj().chargeStage = targetDesc.stage

    def setPowerState(self, powerState):
        if self.tcpSocket.state() == QAbstractSocket.UnconnectedState:
            print( f"{SC.sWarning} No connection with charge station { self.address_data.address, self.address_data.port }" )

        current_stage = self.netObj().chargeStage
        if current_stage == ECS.GetVoltage or current_stage == ECS.GetCurrent:
            if powerState == EPS.on:
                # Включение начинается с отправки напряжения и заканчивается, собственно, включением
                self.netObj().chargeStage = ECS.SetVoltage
            elif powerState == EPS.off:
                self.netObj().chargeStage = ECS.SetPowerOff

    def bytesAvailable(self):
        while self.tcpSocket.canReadLine():
            line = self.tcpSocket.readLine().data().decode().replace( "\n", "" )
            current_stage = self.netObj().chargeStage

            if current_stage == ECS.GetState:
                if line == PSC.NoneState:
                    self.netObj().chargeStage = ECS.SetRemote
                elif line == PSC.RemoteState:
                    self.netObj().chargeStage = ECS.GetVoltage

            elif current_stage == ECS.GetVoltage:
                # Получено значение напряжения, значение возвращается в формате "0.00 V"
                self.voltageFact = float( line.split(" ")[0] )
                self.netObj().chargeStage = ECS.GetCurrent

            elif current_stage == ECS.GetCurrent:
                # Получено значение тока, значение возвращается в формате "0.0 A"
                self.currentFact = float( line.split(" ")[0] )
                self.netObj().chargeStage = ECS.GetVoltage


#########################################################################################################

pwHandlers_byConnType = {
                            BT.EConnectionType.USB       : CUSB_PowerHandler,
                            BT.EConnectionType.TCP_IP    : CTCP_IP_PowerHandler,
                            BT.EConnectionType.Undefined : CUSB_PowerHandler
                        }

class CPowerStation:
    def __init__(self, netObj ):
        CTickManager.addTicker( 1000, self.mainTick )
        CNetObj_Manager.addCallback( EV.ObjPropUpdated, self )
        self.makePowerStation_Handler( netObj )

    def mainTick( self ):
        self.powerStation.mainTick()

    def ObjPropUpdated( self, cmd ):
        powerNodeNO = self.netObj()
        if not isSelfEvent( cmd, powerNodeNO ): return

        if cmd.sPropName == SGT.SGA.chargeAddress:
            self.makePowerStation_Handler( powerNodeNO )

        if cmd.sPropName == SGT.SGA.powerState:
            self.powerStation.setPowerState( cmd.value )

    def makePowerStation_Handler(self, netObj):
        powerStationType = pwHandlers_byConnType.get( netObj.chargeAddress._type )
        self.powerStation = powerStationType()
        self.powerStation.netObj = weakref.ref( netObj )
        self.powerStation.address_data = netObj.chargeAddress.data