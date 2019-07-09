import math

from PyQt5.QtCore import pyqtSlot, QTimer

from Lib.Common.Agent_NetObject import s_position, s_edge, s_angle,agentsNodeCache
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Common.TreeNode import CTreeNodeCache
from Lib.Common.GraphUtils import tEdgeKeyToStr, getEdgeCoords, getAgentAngle
from Lib.Common import StorageGraphTypes as SGT
from Lib.Common.Vectors import Vector2

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
        cls.AgentsMove_Timer.setInterval( 5 )
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

        angle, bReverse = getAgentAngle(agentNO.graphRootNode().nxGraph, tEdgeKey, agentNO.angle)
        agentNO.angle = angle

    @classmethod
    def move( cls, agentNO ):
        if agentNO.route == "":
            return

        nodes_route = agentNO.route.split(",")

        new_pos = agentNO.position + 1

        if new_pos > 100:
            newIDX = agentNO.route_idx + 1

            if newIDX >= len( nodes_route )-1:
                agentNO.route_idx = 0
                agentNO.route = ""
                return

            agentNO.position = new_pos % 100
            tEdgeKey = ( nodes_route[ newIDX ], nodes_route[ newIDX + 1 ] )
            agentNO.edge = tEdgeKeyToStr( tEdgeKey )
            agentNO.route_idx = newIDX
        else:
            agentNO.position = new_pos

        cls.calcAgentAngle( agentNO )

    @classmethod
    def moveAgents( cls ):
        for agentNO in cls.agentsNode().children:
            cls.move( agentNO )
