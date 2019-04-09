import math

from PyQt5.QtCore import pyqtSlot, QTimer

from Lib.Common.Agent_NetObject import s_position, s_edge, s_angle,agentsNodeCache
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Common.TreeNode import CTreeNodeCache
from Lib.Common.GraphUtils import getUnitVector, getUnitVector_RadAngle, getUnitVector_DegAngle, getUnitVector_FromDegAngle, tEdgeKeyToStr, getEdgeCoords
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
        x1, y1, x2, y2 = getEdgeCoords( nxGraph, tEdgeKey )

        edge_vec = ( x2 - x1, - (y2 - y1) ) #берём отрицательное значение "y" тк, значения по оси "y" увеличиваются по направлению вниз
        edge_unit_vec = getUnitVector( *edge_vec )
        
        s_EdgeType = nxGraph.edges()[ tEdgeKey ].get( SGT.s_widthType )
        railType = SGT.railType( s_EdgeType )

        agent_unit_vec = getUnitVector_FromDegAngle( agentNO.angle )

        #Если рельс широкий, используем для рассчёта повернутый на -90 градусов вектор грани,
        #так как направление "вперёд" для челнока на широком рельсе это вектор челнока, повернутый на +90 градусов
        #поворачиваем вектор грани, а не вектор челнока для удобства рассчёта, матрица поворота ([0,1],[-1,0])
        if railType == SGT.EWidthType.Narrow:
            r_unit_vec = edge_unit_vec
        elif railType == SGT.EWidthType.Wide:
            r_unit_vec = (edge_unit_vec[1], -edge_unit_vec[0])
        
        cos = r_unit_vec[0] * agent_unit_vec[0] + r_unit_vec[1] * agent_unit_vec[1] #так как вектора единичные достаточно скалярного произведения
        rAngle = math.acos( min( max( -1, cos), 1) ) #компенсация ошибок точности, если abs(cos) > 1
        
        if rAngle < math.pi/4 :
            agentNO.angle = getUnitVector_DegAngle( *r_unit_vec )
        elif rAngle > math.pi * 3/4:
            agentNO.angle = getUnitVector_DegAngle( -r_unit_vec[0], -r_unit_vec[1] )

    @classmethod
    def move( cls, agentNO ):
        if agentNO.route == "":
            return

        nodes_route = agentNO.route.split(",")

        new_pos = agentNO.position + 1

        if new_pos > 100:
            newIDX = agentNO.route_idx + 1

            if newIDX >= len( nodes_route ):
                agentNO.route_idx = 0
                agentNO.route = ""
                return

            agentNO.position = new_pos % 100
            tEdgeKey = ( nodes_route[ agentNO.route_idx ], nodes_route[ newIDX ] )
            agentNO.edge = tEdgeKeyToStr( tEdgeKey )
            agentNO.route_idx = newIDX

            ##remove##
            # edges_route = edges_route[1::]
            # if len(edges_route) != 0:
            #     agentNO.edge = tEdgeKeyToStr(edges_route[0])
            #     agentNO.route = str ( edges_route )
            #     agentNO.position = new_pos % 100
            # else:
            #     agentNO.route = ""
            #     agentNO.position = 100

        else:
            agentNO.position = new_pos

        cls.calcAgentAngle( agentNO )

    @classmethod
    def moveAgents( cls ):
        for agentNO in cls.agentsNode().children:
            cls.move( agentNO )
