import numpy as np

from PyQt5.QtCore import pyqtSlot, QTimer

from Lib.Common.Agent_NetObject import s_position, s_edge, s_angle,agentsNodeCache
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Common.TreeNode import CTreeNodeCache
from Lib.Common.GraphUtils import getUnitVector, getUnitVector_RadAngle, getUnitVector_DegAngle, getUnitVector_FromDegAngle, tEdgeKeyToStr
from Lib.Common import StorageGraphTypes as SGT

class CAgents_Move_Manager():
    @classmethod
    def checkAgentsIsControlled( cls, uid ):
        if len(cls.ControlledAgents) == 0:
            return True
        
        if uin in cls.ControlledAgents.index:
            return True
        
        return False

    @classmethod
    def init( cls ):
        cls.ControlledAgents = []

        CNetObj_Manager.addCallback( EV.ObjPropUpdated, cls.OnPropUpdate )

        cls.AgentsMove_Timer = QTimer()
        cls.AgentsMove_Timer.setInterval(5)
        cls.AgentsMove_Timer.timeout.connect( cls.moveAgents )
        cls.AgentsMove_Timer.start()

        cls.agentsNode = agentsNodeCache()

    @classmethod
    def OnPropUpdate( cls, netCmd ):
        if not cls.checkAgentsIsControlled( netCmd.Obj_UID ):
            return

        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID, genAssert=True )

    @classmethod
    def calcAgentAngle( cls, agentNO ):
        tEdgeKey = agentNO.isOnTrack()
        
        if tEdgeKey is None:
            agentNO.angle = 0
            return

        nxGraph = agentNO.graphRootNode().nxGraph
        nodeID_1, nodeID_2 = tEdgeKey[0], tEdgeKey[1]

        x1 = nxGraph.nodes()[ nodeID_1 ][SGT.s_x]
        y1 = nxGraph.nodes()[ nodeID_1 ][SGT.s_y]
        
        x2 = nxGraph.nodes()[ nodeID_2 ][SGT.s_x]
        y2 = nxGraph.nodes()[ nodeID_2 ][SGT.s_y]

        edge_vec = np.array( [x2,y2], float ) - np.array( [x1,y1], float )
        # edge_vec = np.array( [x2-x1,y2-y1], float ) )

        edge_vec[1] = - edge_vec[1] #берём отрицательное значение тк, значения по оси "y" увеличиваются по направлению вниз
        edge_unit_vec = getUnitVector( *edge_vec )
        
        s_EdgeType = nxGraph.edges()[ (nodeID_1, nodeID_2) ].get( SGT.s_widthType )
        railType = SGT.railType( s_EdgeType )

        agent_unit_vec = getUnitVector_FromDegAngle( agentNO.angle )

        minus90_matrix = np.array( [[0, 1], [-1, 0]], float )

        if railType == SGT.EWidthType.Narrow:
            r_unit_vec = edge_unit_vec
        elif railType == SGT.EWidthType.Wide:
            r_unit_vec = minus90_matrix.dot( edge_unit_vec )
        
        cos = np.dot(r_unit_vec, agent_unit_vec)
        rAngle = np.arccos( cos )
        
        if rAngle < np.pi/4 :
            agentNO.angle = getUnitVector_DegAngle( *r_unit_vec )
        elif rAngle > np.pi * 3/4:
            agentNO.angle = getUnitVector_DegAngle( *(-r_unit_vec) )

    @classmethod
    def move( cls, agentNO ):
        if agentNO.route == "":
            return

        edges_route = eval(agentNO.route)
        new_pos = agentNO.position + 1

        if new_pos > 100:
            edges_route = edges_route[1::]
            if len(edges_route) != 0:
                agentNO.edge = tEdgeKeyToStr(edges_route[0])
                agentNO.route = str ( edges_route )
                agentNO.position = new_pos % 100
            else:
                agentNO.route = ""
                agentNO.position = 100
        else:
            agentNO.position = new_pos

        cls.calcAgentAngle( agentNO )

    @classmethod
    def moveAgents( cls ):
        for agentNO in cls.agentsNode().children:
            cls.move( agentNO )
