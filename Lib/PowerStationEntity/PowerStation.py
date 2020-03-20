import weakref
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


class CBase_PowerHandler:
    def __init__(self, netObj):
        self.netObj = weakref.ref( netObj )
    
    @property
    def address_data(self):
        return self.netObj().chargeAddress.data 

class CUSB_PowerHandler(CBase_PowerHandler):
    
    def mainTick(self, netObj):
        pass
    
    def setPowerState(self, powerState):
        CU.controlCharge( powerState, self.address_data )

    def __del__(self):
        CU.controlCharge( PST.EChargeState.off, self.address_data )


class CTCP_IP_PowerHandler(CBase_PowerHandler):
    def __init__(self, netObj):
        super().__init__( netObj )
        self.tcpSocket = QTcpSocket()
        self.tcpSocket.readyRead.connect( self.bytesAvailable )

        self.voltageMax = 0
        self.currentMax = 0

        self.voltageFact = 0
        self.currentFact = 0

    def __del__(self):
        stage = self.netObj().chargeStage
        if stage == PST.EChargeStage.GetVoltage or stage == PST.EChargeStage.GetCurrent:
            self.tcpSocket.write( "OUTP OFF" )
        self.tcpSocket.disconnect()
    
    def mainTick(self):
        if self.tcpSocket.state() == QAbstractSocket.UnconnectedState:
            self.tcpSocket.connectToHost( self.address_data.address, self.address_data.port )

            if self.tcpSocket.waitForConnected(100):
                self.netObj().chargeStage = PST.EChargeStage.GetState
            else:
                print( f"{SC.sWarning} No connection with charge station { self.address_data.address, self.address_data.port }" )
        
        elif self.tcpSocket.state() == QAbstractSocket.ConnectedState:
            current_stage = self.netObj().chargeStage
            target_stage, target_power_state, data = None, None, None

            if current_stage == PST.EChargeStage.GetState:
                # Получить статус удаленного управления
                data = "SYST:LOCK:OWN?"
            
            elif current_stage == PST.EChargeStage.SetRemote:
                # Переключить на удаленное управление
                data, target_stage = "SYST:LOCK:STAT 1", PST.EChargeStage.SetReset

            elif current_stage == PST.EChargeStage.SetReset:
                # Выполнить сброс устройства для переключения в режим удаленного управления
                data, target_stage = "*RST", PST.EChargeStage.GetState

            elif current_stage == PST.EChargeStage.GetVoltage:
                # Отправить запрос на получение напряжения
                data = "MEAS:VOLT?"

            elif current_stage == PST.EChargeStage.GetCurrent:
                # Отправить запрос на получение тока
                data = "MEAS:CURR?"

            elif current_stage == PST.EChargeStage.SetPowerOff:
                # Отключить выход
                data = "OUTP OFF"
                target_power_state = PST.EChargeState.off
                target_stage = PST.EChargeStage.GetVoltage

            elif current_stage == PST.EChargeStage.SetVoltage:
                # Установить напряжение на выходе
                # sprintf( data, "VOLT %d.%d", mVoltageMax / 10, mVoltageMax % 10 );
                # mSocket.write( data, strlen( data ) );
                data, target_stage = f"VOLT { self.voltageMax / 10 }", PST.EChargeStage.SetCurrent

            elif current_stage == PST.EChargeStage.SetCurrent:
                # Установить ток на выходе
                # sprintf( data, "CURR %d.%d", mCurrentMax / 10, mCurrentMax % 10 );
                # mSocket.write( data, strlen( data ) );
                data, target_stage = f"CURR { self.currentMax / 10 }", PST.EChargeStage.SetPowerOn

            elif current_stage == PST.EChargeStage.SetPowerOn:
                # Включить выход
                data, target_stage = "OUTP ON", PST.EChargeStage.GetVoltage

            if data is not None: self.tcpSocket.write( data.encode() )
            if target_power_state is not None: self.netObj().powerState = target_power_state
            if target_stage is not None: self.netObj().chargeStage = target_stage

    def setPowerState(self, powerState):
        current_stage = self.netObj().chargeStage
        if current_stage == PST.EChargeStage.GetVoltage or current_stage == PST.EChargeStage.GetCurrent:
            if powerState == PST.EChargeState.on:
                # Включение начинается с отправки напряжения и заканчивается, собственно, включением
                self.netObj().chargeStage = PST.EChargeStage.SetVoltage
            elif powerState == PST.EChargeState.off:
                self.netObj().chargeStage = PST.EChargeStage.SetPowerOff

    def bytesAvailable(self):
        while self.tcpSocket.canReadLine():
            line = self.tcpSocket.readLine().data().decode().replace( "\n", "" )
            print(line)
            current_stage = self.netObj().chargeStage

            if current_stage == PST.EChargeStage.GetState:
                if line == "NONE":
                    self.netObj().chargeStage = PST.EChargeStage.SetRemote
                elif line == "REMOTE":
                    self.netObj().chargeStage = PST.EChargeStage.GetVoltage

            elif current_stage == PST.EChargeStage.GetVoltage:
                # Получено значение напряжения, значение возвращается в формате "0.00 V"
                self.voltageFact = float( line.split(" ")[0] ) * 10
                self.netObj().chargeStage = PST.EChargeStage.GetCurrent

            elif current_stage == PST.EChargeStage.GetCurrent:
                # Получено значение тока, значение возвращается в формате "0.0 A"
                self.currentFact = float( line.split(" ")[0] ) * 10
                self.netObj().chargeStage = PST.EChargeStage.GetVoltage

pwHandlers_byConnType = {
                            BT.EConnectionType.USB    : CUSB_PowerHandler,
                            BT.EConnectionType.TCP_IP : CTCP_IP_PowerHandler
                        }

#########################################################################################################

class CPowerStation:
    def __init__(self, netObj ):
        CTickManager.addTicker( 1000, self.mainTick )
        CNetObj_Manager.addCallback( EV.ObjPropUpdated, self )

        powerStationType = pwHandlers_byConnType.get( netObj.chargeAddress._type )
        self.powerStation = powerStationType( netObj )

    def mainTick( self ):
        self.powerStation.mainTick()

    def ObjPropUpdated( self, cmd ):
        powerNodeNO = self.netObj()
        if not isSelfEvent( cmd, powerNodeNO ): return

        if cmd.sPropName == SGT.SGA.chargeAddress:
            powerStationType = pwHandlers_byConnType.get( powerNodeNO.chargeAddress._type )
            self.powerStation = powerStationType( powerNodeNO.chargeAddress )

        if cmd.sPropName == SGT.SGA.powerState:
            self.powerStation.setPowerState( cmd.value )