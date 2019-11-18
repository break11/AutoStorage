from collections import deque

import Lib.GraphEntity.StorageGraphTypes as SGT
from Lib.AgentEntity.AgentServer_Link import CAgentServer_Link
import Lib.AgentEntity.AgentDataTypes as ADT

class CFakeAgentLink( CAgentServer_Link ):
    def __init__( self, agentN ):
        super().__init__( agentN = agentN )

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
        self.OD_OP_Data  = ADT.SOD_OP_Data()
