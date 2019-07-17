from collections import deque

from Lib.AgentProtocol.AgentServer_Link import CAgentServer_Link

class CFakeAgentLink( CAgentServer_Link ):
    def __init__( self, agentN ):
        super().__init__( agentN = agentN, bIsServer = False )

        self.tasksList = deque()
        self.BS_Answer = "S,43.2V,39.31V,47.43V,-0.06A"
        self.TS_Answer = "24,29,29,29,29,25,25,25,25"
        
        self.currentTask = None
        self.currentWheelsOrientation = ''
        self.currentDirection = ''
        self.odometryCounter = 0
        self.distanceToPass = 0
        self.dpTicksDivider = 0
        self.bEmergencyStop = False
