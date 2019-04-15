import math

from PyQt5.QtCore import pyqtSlot, QTimer

from Lib.Common.Agent_NetObject import s_position, s_edge, s_angle,agentsNodeCache
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Common.TreeNode import CTreeNodeCache
from Lib.Common.GraphUtils import tEdgeKeyToStr, getEdgeCoords
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

        nxGraph = agentNO.graphRootNode().nxGraph
        x1, y1, x2, y2 = getEdgeCoords( nxGraph, tEdgeKey )

        edge_vec = Vector2( x2 - x1, - (y2 - y1) ) #берём отрицательное значение "y" тк, значения по оси "y" увеличиваются по направлению вниз
        
        s_EdgeType = nxGraph.edges()[ tEdgeKey ].get( SGT.s_widthType )
        railType = SGT.railType( s_EdgeType )

        agent_vec = Vector2.fromAngle( math.radians( agentNO.angle ) )

        #Если рельс широкий, используем для рассчёта повернутый на -90 градусов вектор грани,
        #так как направление "вперёд" для челнока на широком рельсе это вектор челнока, повернутый на +90 градусов
        #поворачиваем вектор грани, а не вектор челнока для удобства рассчёта, матрица поворота ([0,1],[-1,0])

        if railType == SGT.EWidthType.Narrow:
            r_vec = edge_vec
        elif railType == SGT.EWidthType.Wide:
            r_vec = edge_vec.rotate( math.pi/2 )
        
        rAngle = agent_vec.angle( r_vec )
        
        if rAngle < math.pi/4 :
            agentNO.angle = math.degrees( r_vec.selfAngle() )
        elif rAngle > math.pi * 3/4:
            agentNO.angle = math.degrees( r_vec.rotate( math.pi ).selfAngle() )

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
