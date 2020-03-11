from collections import deque

import Lib.GraphEntity.StorageGraphTypes as SGT
from Lib.AgentEntity.AgentServer_Link import CAgentServer_Link
import Lib.AgentEntity.AgentDataTypes as ADT

from .FakeAgentThread import CFakeAgentThread

class CFakeAgentLink( CAgentServer_Link ):
    def __init__(self, netObj ):
        super().__init__( agentN = netObj.name )

        self.tasksList = deque()
                
        self.currentTask = None
        self.currentWheelsOrientation = SGT.EWidthType.Narrow
        self.currentDirection = ''
        self.distanceToPass = 0
        self.dpTicksDivider = 0
        self.BL_BU_Time = 0
        self.bEmergencyStop = False
        self.bCharging = False
        self.bErrorState = False

        self.temperatureState = ADT.STS_Data( 24,29,29,29,29,25,25,25,25 )
        self.batteryState = ADT.SBS_Data( ADT.EAgentBattery_Type.Supercap, 43.2, 39.31, 47.43, 00.9, 00.4 )
        self.OdometerData  = ADT.SOdometerData( bUndefined=False )

    def connect( self, ip, port ):
        if self.isConnected(): return

        FA_Thread = CFakeAgentThread()
        FA_Thread.init( self, ip, port )
        self.socketThreads.append( FA_Thread )
                    
        FA_Thread.finished.connect( self.thread_Finihsed )
        FA_Thread.start()
