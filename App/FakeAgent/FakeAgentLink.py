from collections import deque

from Lib.AgentProtocol.AgentServer_Link import CAgentServer_Link
from Lib.AgentProtocol.AgentDataTypes import SAgent_BatteryState, EAgentBattery_Type, SOD_OP_Data

class CFakeAgentLink( CAgentServer_Link ):
    def __init__( self, agentN ):
        super().__init__( agentN = agentN, bIsServer = False )

        self.tasksList = deque()
        self.TS_Answer = "24,29,29,29,29,25,25,25,25"
        
        self.currentTask = None
        self.currentWheelsOrientation = ''
        self.currentDirection = ''
        self.distanceToPass = 0
        self.dpTicksDivider = 0
        self.bEmergencyStop = False
        self.bCharging = False

        self.batteryState = SAgent_BatteryState( EAgentBattery_Type.Supercap, 43.2, 39.31, 47.43, 00.9, 00.4 )
        self.OD_OP_Data  = SOD_OP_Data()
