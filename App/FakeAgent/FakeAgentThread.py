from collections import deque
import datetime
import weakref
import sys, time

from PyQt5.QtNetwork import QAbstractSocket, QTcpSocket
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event
from Lib.AgentProtocol.AgentServerPacket import CAgentServerPacket
from Lib.AgentProtocol.AgentLogManager import ALM
from Lib.AgentProtocol.AgentServer_Net_Thread import CAgentServer_Net_Thread
from Lib.AgentProtocol.AgentDataTypes import SFakeAgent_DevPacketData, SAgent_BatteryState

DP_DELTA_PER_CYCLE = 50 # send to server a message each fake 5cm passed
DP_TICKS_PER_CYCLE = 7  # pass DP_DELTA_PER_CYCLE millimeters each DP_TICKS_PER_CYCLE milliseconds
BS_DEC_PER_CYCLE   = DP_DELTA_PER_CYCLE * 0.0001

taskCommands = [ EAgentServer_Event.SequenceBegin,
                 EAgentServer_Event.SequenceEnd,
                 EAgentServer_Event.WheelOrientation,
                 EAgentServer_Event.BoxLoad,
                 EAgentServer_Event.BoxUnload,
                 EAgentServer_Event.DistancePassed,
                 EAgentServer_Event.EmergencyStop
               ]

class CFakeAgentThread( CAgentServer_Net_Thread ):
    # местная ф-я обработки пакета, если он признан актуальным
    # на часть команд отвечаем - часть заносим в taskList
    def processRxPacket(self, cmd):
        FAL = self.agentLink()
        if cmd.event == EAgentServer_Event.HelloWorld:
            # cmd = self.genPacket( event = EAgentServer_Event.HelloWorld, data = str( self.fakeAgentLink().last_RX_packetN ) )
            # cmd.packetN = 0
            # FAL.pushCmd( cmd, bPut_to_TX_FIFO = False, bReMap_PacketN=False )
            FAL.pushCmd( self.genPacket( event = EAgentServer_Event.HelloWorld, data = str( FAL.last_RX_packetN ) ) )
        elif cmd.event == EAgentServer_Event.TaskList:
            FAL.pushCmd( self.genPacket( event = EAgentServer_Event.TaskList, data = str( len( FAL.tasksList ) ) ) )
        elif cmd.event == EAgentServer_Event.BatteryState:
            FAL.pushCmd( self.genPacket( event = EAgentServer_Event.BatteryState, data = FAL.batteryState.toString() ) )
        elif cmd.event == EAgentServer_Event.TemperatureState:
            FAL.pushCmd( self.genPacket( event = EAgentServer_Event.TemperatureState, data = FAL.TS_Answer ) )
        elif cmd.event == EAgentServer_Event.OdometerDistance:
            FAL.pushCmd( self.genPacket( event = EAgentServer_Event.OdometerDistance, data = "U" ) )
        elif cmd.event == EAgentServer_Event.BrakeRelease:
            FAL.bEmergencyStop = False
            FAL.pushCmd( self.genPacket( event = EAgentServer_Event.BrakeRelease, data = "FW" ) )
        elif cmd.event == EAgentServer_Event.PowerOn or cmd.event == EAgentServer_Event.PowerOff:
            FAL.pushCmd( self.genPacket( event = EAgentServer_Event.NewTask, data = "ID" ) )
        elif cmd.event == EAgentServer_Event.FakeAgentDevPacket:
            FA_DPD = SFakeAgent_DevPacketData.fromString( cmd.data )
            if FA_DPD.bChargeOff:
               FAL.batteryState.S_V = SAgent_BatteryState.max_S_U
        elif cmd.event in taskCommands:
            FAL.tasksList.append( cmd )

    def doWork( self ):
        FAL = self.agentLink()
        
        if self.findEvent_In_TasksList( EAgentServer_Event.EmergencyStop ):
            FAL.tasksList.clear()
            FAL.currentTask = None
            FAL.bEmergencyStop = True
            ALM.doLogString( FAL, "Emergency Stop !!!!" )
            return

        if FAL.currentTask:
            if FAL.currentTask.event == EAgentServer_Event.SequenceBegin:
                if self.findEvent_In_TasksList( EAgentServer_Event.SequenceEnd ):
                    self.startNextTask()

            elif FAL.currentTask.event == EAgentServer_Event.SequenceEnd:
                self.startNextTask()

            elif FAL.currentTask.event == EAgentServer_Event.BoxLoad:
                FAL.pushCmd( self.genPacket( event = EAgentServer_Event.NewTask, data = "BL,L" ) )
                self.startNextTask()

            elif FAL.currentTask.event == EAgentServer_Event.BoxUnload:
                FAL.pushCmd( self.genPacket( event = EAgentServer_Event.NewTask, data = "BU,L" ) )
                self.startNextTask()

            elif FAL.currentTask.event == EAgentServer_Event.WheelOrientation:
                newWheelsOrientation = FAL.currentTask.data[ 0:1 ]
                FAL.odometryCounter = 0
                # send an "odometry resetted" to server
                FAL.pushCmd( self.genPacket( event = EAgentServer_Event.OdometerZero ) )

                FAL.currentWheelsOrientation = FAL.currentTask.data[ 0:1 ]
                # will be 'N' for narrow, 'W' for wide, or emtpy if uninited
                FAL.pushCmd( self.genPacket( event = EAgentServer_Event.NewTask, data = "WO" ) )

                self.startNextTask()

            elif FAL.currentTask.event == EAgentServer_Event.DistancePassed:

                if FAL.dpTicksDivider < DP_TICKS_PER_CYCLE:
                    FAL.dpTicksDivider = FAL.dpTicksDivider + 1

                elif FAL.dpTicksDivider == DP_TICKS_PER_CYCLE:
                    FAL.batteryState.S_V = max( FAL.batteryState.S_V - BS_DEC_PER_CYCLE, 0 )
                    FAL.dpTicksDivider = 0
                    if FAL.distanceToPass > 0:
                        FAL.distanceToPass = FAL.distanceToPass - DP_DELTA_PER_CYCLE
                        if FAL.currentDirection == 'F':
                            FAL.odometryCounter = FAL.odometryCounter + DP_DELTA_PER_CYCLE
                        else:
                            FAL.odometryCounter = FAL.odometryCounter - DP_DELTA_PER_CYCLE
                        FAL.pushCmd( self.genPacket( event = EAgentServer_Event.OdometerDistance, data = str( FAL.odometryCounter ) ) )

                    elif FAL.distanceToPass <= 0:
                        FAL.distanceToPass = 0
                        FAL.pushCmd( self.genPacket( event = EAgentServer_Event.DistanceEnd ) )
                        self.startNextTask()

        if len(FAL.tasksList) and FAL.currentTask is None:
            self.startNextTask()

    def startNextTask(self):
        FAL = self.agentLink()

        if len(FAL.tasksList):
            FAL.currentTask = FAL.tasksList.popleft()
            #self.sendPacketToServer('@NT:{:s}'.format(FAL.currentTask[1:1+2].decode()).encode('utf-8'))
            ALM.doLogString( FAL, f"Starting new task: {FAL.currentTask}" )

            if FAL.currentTask.event == EAgentServer_Event.DistancePassed:
                FAL.distanceToPass   = int( FAL.currentTask.data[ 0:6 ] )
                FAL.currentDirection = FAL.currentTask.data[ 7:8 ] # F or R
        else:
            FAL.currentTask = None
            ALM.doLogString( FAL, "All tasks done!" )
            FAL.pushCmd( CAgentServerPacket( event=EAgentServer_Event.NewTask, data="ID" ) )

    def findEvent_In_TasksList(self, event):
        for cmd in self.agentLink().tasksList:
            if cmd.event == event:
                return True
        return False
