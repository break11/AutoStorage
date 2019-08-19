from collections import deque
import datetime
import weakref
import sys, time

from PyQt5.QtNetwork import QAbstractSocket, QTcpSocket
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event as AEV
from Lib.AgentProtocol.AgentServerPacket import CAgentServerPacket
from Lib.AgentProtocol.AgentLogManager import ALM
from Lib.AgentProtocol.AgentServer_Net_Thread import CAgentServer_Net_Thread
from Lib.AgentProtocol.AgentDataTypes import SFakeAgent_DevPacketData, SAgent_BatteryState, SHW_Data, EAgentBattery_Type, TeleEvents

DP_DELTA_PER_CYCLE   = 50 # send to server a message each fake 5cm passed
DP_TICKS_PER_CYCLE   = 7  # pass DP_DELTA_PER_CYCLE millimeters each DP_TICKS_PER_CYCLE milliseconds
BS_DEC_PER_CYCLE     = DP_DELTA_PER_CYCLE * 0.0001
DP_CHARGE_PER_CYCLE  = 0.005
BL_BU_TIME           = 14000 #время погрузки/разгрузки коробки, мс
BL_BU_TIME_PER_CYCLE = 1.2   #время погрузки за один тик, мс

taskCommands = [ AEV.SequenceBegin,
                 AEV.SequenceEnd,
                 AEV.WheelOrientation,
                 AEV.BoxLoad,
                 AEV.BoxUnload,
                 AEV.DistancePassed,
                 AEV.EmergencyStop,
                 AEV.PowerDisable,
                 AEV.PowerEnable
               ]

NotIgnoreEvents = TeleEvents.union( { AEV.PowerEnable } )

class CFakeAgentThread( CAgentServer_Net_Thread ):
    # местная ф-я обработки пакета, если он признан актуальным
    # на часть команд отвечаем - часть заносим в taskList
    def processRxPacket(self, cmd):
        FAL = self.agentLink()

        if FAL.bErrorState and cmd.event not in NotIgnoreEvents:
            data = f":{cmd.data}" if cmd.data is not None else ""
            cmd_str = cmd.event.toStr()[1:]
            FAL.pushCmd( self.genPacket( event = AEV.Warning_, data = f"##COMMAND IN ERROR STATE IGNORED: {cmd_str}{data}" ) )
            return

        if cmd.event == AEV.HelloWorld:
            # cmd = self.genPacket( event = AEV.HelloWorld, data = SHW_Data( FAL.last_RX_packetN ).toString() )
            # cmd.packetN = 0
            # FAL.pushCmd( cmd, bPut_to_TX_FIFO = False, bReMap_PacketN=False )

            FAL.pushCmd( self.genPacket( event = AEV.HelloWorld, data = SHW_Data( FAL.last_RX_packetN ).toString() ) )

        elif cmd.event == AEV.TaskList:
            FAL.pushCmd( self.genPacket( event = AEV.TaskList, data = str( len( FAL.tasksList ) ) ) )

        elif cmd.event == AEV.BatteryState:
            FAL.pushCmd( self.genPacket( event = AEV.BatteryState, data = FAL.batteryState.toString() ) )

        elif cmd.event == AEV.TemperatureState:
            FAL.pushCmd( self.genPacket( event = AEV.TemperatureState, data = FAL.TS_Answer ) )

        elif cmd.event == AEV.OdometerDistance:
            FAL.pushCmd( self.genPacket( event = AEV.OdometerDistance, data = FAL.OD_OP_Data.toString() ) )

        elif cmd.event == AEV.OdometerPassed:
            FAL.pushCmd( self.genPacket( event = AEV.OdometerPassed, data = FAL.OD_OP_Data.toString() ) )

        elif cmd.event == AEV.BrakeRelease:
            FAL.bErrorState = False
            FAL.bEmergencyStop = False
            FAL.pushCmd( self.genPacket( event = AEV.BrakeRelease, data = "FW" ) )

        # elif cmd.event == AEV.PowerEnable:
            # FAL.pushCmd( self.genPacket( event = AEV.NewTask, data = "ID" ) )

        elif cmd.event == AEV.PowerDisable:
            FAL.tasksList.clear()
            FAL.bErrorState = True

        elif cmd.event == AEV.ChargeMe:
            FAL.pushCmd( self.genPacket( event = AEV.ChargeBegin ) )
            FAL.bCharging = True

        if cmd.event in taskCommands:
            FAL.tasksList.append( cmd )

    def doWork( self ):
        global NotIgnoreEvents
        FAL = self.agentLink()
        
        # зарядка суперконденсаторов до максимального значения
        if FAL.bCharging:
            if FAL.batteryState.S_V < SAgent_BatteryState.max_S_U:
                FAL.batteryState.S_V += DP_CHARGE_PER_CYCLE
            else:
                FAL.bCharging = False
                FAL.pushCmd( self.genPacket( event = AEV.ChargeEnd ) )

        if self.findEvent_In_TasksList( AEV.EmergencyStop ):
            FAL.tasksList.clear()
            FAL.currentTask = None
            FAL.bEmergencyStop = True
            ALM.doLogString( FAL, "Emergency Stop !!!!" )
            return

        if FAL.currentTask:
            if FAL.currentTask.event == AEV.PowerDisable:
                FAL.batteryState.PowerType = EAgentBattery_Type.N
                NotIgnoreEvents -= { AEV.BrakeRelease }
                FAL.pushCmd( self.genPacket( event = AEV.Error, data = f"Power Disable Fake Agent Err" ) ) #HACK реальный агент при выключении становится в состояние ошибки
                self.startNextTask()

            elif FAL.currentTask.event == AEV.PowerEnable:
                FAL.batteryState.PowerType = EAgentBattery_Type.Supercap
                NotIgnoreEvents.add( AEV.BrakeRelease )
                FAL.pushCmd( self.genPacket( event = AEV.Error, data = f"Power Enable Fake Agent Err" ) ) #HACK реальный агент при включении становится в состояние ошибки
                self.startNextTask()

            elif FAL.currentTask.event == AEV.SequenceBegin:
                if self.findEvent_In_TasksList( AEV.SequenceEnd ):
                    self.startNextTask()

            elif FAL.currentTask.event == AEV.SequenceEnd:
                self.startNextTask()

            elif (FAL.currentTask.event == AEV.BoxLoad) or (FAL.currentTask.event == AEV.BoxUnload):
                cmd_str = FAL.currentTask.event.toStr()[1:]

                if FAL.BL_BU_Time < BL_BU_TIME:
                    if FAL.BL_BU_Time == 0: FAL.pushCmd( self.genPacket( event = AEV.NewTask, data = f"{cmd_str},{FAL.currentTask.data}" ) )
                    FAL.BL_BU_Time += BL_BU_TIME_PER_CYCLE
                else:
                    FAL.BL_BU_Time = 0
                    self.startNextTask()

            # elif FAL.currentTask.event == AEV.BoxUnload:
            #     FAL.pushCmd( self.genPacket( event = AEV.NewTask, data = f"BU,{FAL.currentTask.data}" ) )
            #     self.startNextTask()

            elif FAL.currentTask.event == AEV.WheelOrientation:
                newWheelsOrientation = FAL.currentTask.data[ 0:1 ]
                FAL.OD_OP_Data.bUndefined = False
                FAL.OD_OP_Data.nDistance = 0
                # send an "odometry resetted" to server
                FAL.pushCmd( self.genPacket( event = AEV.OdometerZero ) )

                FAL.currentWheelsOrientation = FAL.currentTask.data[ 0:1 ]
                # will be 'N' for narrow, 'W' for wide, or emtpy if uninited
                FAL.pushCmd( self.genPacket( event = AEV.NewTask, data = "WO" ) )

                self.startNextTask()

            elif FAL.currentTask.event == AEV.DistancePassed:

                if FAL.dpTicksDivider < DP_TICKS_PER_CYCLE:
                    FAL.dpTicksDivider = FAL.dpTicksDivider + 1

                elif FAL.dpTicksDivider == DP_TICKS_PER_CYCLE:
                    FAL.batteryState.S_V = max( FAL.batteryState.S_V - BS_DEC_PER_CYCLE, 0 )
                    FAL.dpTicksDivider = 0
                    if FAL.distanceToPass > 0:
                        FAL.distanceToPass = FAL.distanceToPass - DP_DELTA_PER_CYCLE
                        if FAL.currentDirection == 'F':
                            FAL.OD_OP_Data.nDistance = FAL.OD_OP_Data.nDistance + DP_DELTA_PER_CYCLE
                        else:
                            FAL.OD_OP_Data.nDistance = FAL.OD_OP_Data.nDistance - DP_DELTA_PER_CYCLE
                        
                        FAL.pushCmd( self.genPacket( event = AEV.OdometerDistance, data = FAL.OD_OP_Data.toString() ) )

                    elif FAL.distanceToPass <= 0:
                        FAL.distanceToPass = 0
                        FAL.pushCmd( self.genPacket( event = AEV.DistanceEnd ) )
                        self.startNextTask()

        if len(FAL.tasksList) and FAL.currentTask is None:
            self.startNextTask()

    def startNextTask(self):
        FAL = self.agentLink()

        if len(FAL.tasksList):
            FAL.currentTask = FAL.tasksList.popleft()
            #self.sendPacketToServer('@NT:{:s}'.format(FAL.currentTask[1:1+2].decode()).encode('utf-8'))
            ALM.doLogString( FAL, f"Starting new task: {FAL.currentTask}" )

            if FAL.currentTask.event == AEV.DistancePassed:
                FAL.distanceToPass   = int( FAL.currentTask.data[ 0:6 ] )
                FAL.currentDirection = FAL.currentTask.data[ 7:8 ] # F or R
        else:
            FAL.currentTask = None
            ALM.doLogString( FAL, "All tasks done!" )
            FAL.pushCmd( CAgentServerPacket( event=AEV.NewTask, data="ID" ) )

    def findEvent_In_TasksList(self, event):
        for cmd in self.agentLink().tasksList:
            if cmd.event == event:
                return True
        return False
