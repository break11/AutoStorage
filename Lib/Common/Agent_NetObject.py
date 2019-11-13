
from PyQt5.QtCore import QTimer

from copy import deepcopy
from collections import namedtuple

from Lib.Net.NetObj import CNetObj
from Lib.Common.TreeNode import CTreeNode, CTreeNodeCache
from Lib.Net.NetObj_Manager import CNetObj_Manager
import Lib.Common.GraphUtils as GU
from Lib.Common.Graph_NetObjects import graphNodeCache
from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event as EV
import Lib.AgentProtocol.AgentDataTypes as ADT
import Lib.AgentProtocol.AgentTaskData as ATD
import Lib.AgentProtocol.AgentTaskData as ATD
from Lib.Common import StorageGraphTypes as SGT
from Lib.Common.StrProps_Meta import СStrProps_Meta
from Lib.Common.StrConsts import SC
from Lib.Common.SerializedList import CStrList

s_Agents = "Agents"

class SAgentProps( metaclass = СStrProps_Meta ):
    edge            = None
    position        = None
    route           = None
    route_idx       = None
    angle           = None
    odometer        = None
    status          = None
    auto_control    = None
    connectedTime   = None
    connectedStatus = None
    task_list       = None
    task_idx        = None
    cmd_PE          = None
    cmd_PD          = None
    cmd_BR          = None
    cmd_ES          = None
    cmd_BL_L        = None
    cmd_BL_R        = None
    cmd_BU_L        = None
    cmd_BU_R        = None
    cmd_BA          = None
    cmd_CM          = None
    RTele           = None
    BS              = None
    TS              = None

SAP = SAgentProps

cmdDesc = namedtuple( "cmdDesc", "event data" )

cmdProps = { SAP.cmd_PE   : cmdDesc( event=EV.PowerEnable,    data=None),
             SAP.cmd_PD   : cmdDesc( event=EV.PowerDisable,   data=None),
             SAP.cmd_BR   : cmdDesc( event=EV.BrakeRelease,   data=None),
             SAP.cmd_ES   : cmdDesc( event=EV.EmergencyStop,  data=None),
             SAP.cmd_BL_L : cmdDesc( event=EV.BoxLoad,        data=SGT.ESide.Left  ),
             SAP.cmd_BL_R : cmdDesc( event=EV.BoxLoad,        data=SGT.ESide.Right ),
             SAP.cmd_BU_L : cmdDesc( event=EV.BoxUnload,      data=SGT.ESide.Left  ),
             SAP.cmd_BU_R : cmdDesc( event=EV.BoxUnload,      data=SGT.ESide.Right ),
             SAP.cmd_BA   : cmdDesc( event=EV.BoxLoadAborted, data=None),
             SAP.cmd_CM   : cmdDesc( event=EV.ChargeMe,       data=None),
            }

cmdDesc_To_Prop = {} #type:ignore
for k, v in cmdProps.items():
    cmdDesc_To_Prop[ v ] = k

cmdProps_keys = cmdProps.keys()

def agentsNodeCache():
    return CTreeNodeCache( baseNode = CNetObj_Manager.rootObj, path = s_Agents )

def queryAgentNetObj( name ):
    props = deepcopy( CAgent_NO.def_props )
    return agentsNodeCache()().queryObj( sName=name, ObjClass=CAgent_NO, props=props )

class CAgent_NO( CNetObj ):
    def_props = {
                SAP.status: ADT.EAgent_Status.Idle,
                SAP.connectedTime : 0,
                SAP.connectedStatus : ADT.EConnectedStatus.disconnected,
                SAP.auto_control : 1,

                SAP.edge: CStrList(),
                SAP.position: 0,
                SAP.angle : 0.0,
                SAP.odometer : 0,              

                SAP.route: CStrList(),
                SAP.route_idx: 0,
                SAP.task_list : ATD.CTaskList(),
                SAP.task_idx  : 0,

                SAP.cmd_PE   : ADT.EAgent_CMD_State.Done, SAP.cmd_PD   : ADT.EAgent_CMD_State.Done,
                SAP.cmd_BR   : ADT.EAgent_CMD_State.Done, SAP.cmd_ES   : ADT.EAgent_CMD_State.Done,
                SAP.cmd_BL_L : ADT.EAgent_CMD_State.Done, SAP.cmd_BL_R : ADT.EAgent_CMD_State.Done,
                SAP.cmd_BU_L : ADT.EAgent_CMD_State.Done, SAP.cmd_BU_R : ADT.EAgent_CMD_State.Done,
                SAP.cmd_BA   : ADT.EAgent_CMD_State.Done, SAP.cmd_CM   : ADT.EAgent_CMD_State.Done,

                SAP.BS : ADT.SBS_Data.defVal(),
                SAP.TS : ADT.STS_Data.defVal(),

                SAP.RTele : 1
                }
              
    @property
    def nxGraph( self ): return self.graphRootNode().nxGraph

    def __init__( self, name="", parent=None, id=None, saveToRedis=True, props=None, ext_fields=None ):
        self.graphRootNode = graphNodeCache()
        self.lastConnectedTime = 0
        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis, props=props, ext_fields=ext_fields )

        self.tick_Timer = QTimer()
        self.tick_Timer.setInterval( 1000 )
        self.tick_Timer.timeout.connect( self.onTick )
        self.tick_Timer.start()

    def onTick( self ):
        if self.connectedTime == 0:
           self.connectedStatus = ADT.EConnectedStatus.disconnected
        elif self.connectedTime == self.lastConnectedTime:
           self.connectedStatus = ADT.EConnectedStatus.freeze
        else:
           self.connectedStatus = ADT.EConnectedStatus.connected

        self.lastConnectedTime = self.connectedTime

    def ObjPropUpdated( self, netCmd ):
        if netCmd.sPropName == SAP.status:
            if netCmd.value in ADT.errorStatuses:
                self.auto_control = 0

    def isOnTrack( self ):
        if ( not self.edge ) or ( not self.graphRootNode() ):
            return

        tEdgeKey = self.edge.toTuple()

        if len(tEdgeKey) < 2 :
            return
        
        nodeID_1 = tEdgeKey[0]
        nodeID_2 = tEdgeKey[1]

        if not self.nxGraph.has_edge( nodeID_1, nodeID_2 ):
            return
        
        return tEdgeKey

    def isOnNode( self, nodeID = None, nodeType = None ):
        tEdgeKey = self.isOnTrack()
        if not tEdgeKey: return False

        return GU.isOnNode( self.nxGraph, tEdgeKey, self.position, _nodeID=nodeID, _nodeType=nodeType )

    def putToNode( self, nodeID ):        
        if not self.nxGraph.has_node( nodeID ): return

        if GU.nodeType( self.nxGraph, nodeID ) == SGT.ENodeTypes.Terminal: return

        edges = list( self.nxGraph.out_edges( nodeID ) ) + list( self.nxGraph.in_edges( nodeID ) )
        if len( edges ) == 0: return

        tEdgeKey = edges[ 0 ]
        self.edge = CStrList.fromTuple( tEdgeKey )
        self.position = 0 if tEdgeKey[ 0 ] == nodeID else GU.edgeSize( self.nxGraph, tEdgeKey )

    def goToNode( self, targetNode ):
        if not self.nxGraph.has_node( targetNode ): return

        tKey = self.isOnTrack()
        if tKey is None:
            self.putToNode( targetNode )
            return

        startNode = tKey[0]

        if GU.nodeType( self.nxGraph, targetNode ) == SGT.ENodeTypes.Terminal: return

        self.task_list = ATD.CTaskList( elementList=[ ATD.CTask( taskType=ATD.ETaskType.GoToNode, taskData=targetNode ) ] )

    def applyRoute( self, nodes_route ):
        route_size = len(nodes_route)
        if route_size == 0: return

        tKey = self.isOnTrack()
        assert tKey is not None
        assert nodes_route[0] in tKey, "Cant apply route. The position and route do not intersect."

        curEdgeSize = GU.edgeSize( self.nxGraph, tKey )
        
        if route_size == 1:
            if nodes_route[0] == tKey[0]:
                nodes_route = list( reversed(tKey) )
            else:
                nodes_route = list( tKey )
        else:
            # выполнится только одно условие, тк одна из нод tKey присутствует в маршруте ( см. assert выше )
            if tKey[0] not in nodes_route: nodes_route.insert( 0, tKey[0] )
            if tKey[1] not in nodes_route: nodes_route.insert( 0, tKey[1] )

        # перепрыгивание на кратную грань, если челнок стоит на грани противоположной направлению маршрута
        if ( nodes_route[1], nodes_route[0] ) == tKey:
            tKey = tuple( reversed(tKey) )
            self.edge = CStrList.fromTuple( tKey )
            curEdgeSize = GU.edgeSize( self.nxGraph, tKey )
            self.position = curEdgeSize - self.position
        
        # переставляем челнок на вторую грань маршрута, если его позиция на первой грани более 50%
        if ( self.position / curEdgeSize ) > 0.5:
            if len( nodes_route ) > 2:
                nodes_route = nodes_route[1:]
                tKey = ( nodes_route[0], nodes_route[1] )
                self.edge = CStrList.fromTuple( tKey )
                self.position = 0
            else:
                return

        self.route = CStrList( elementList = nodes_route )

        return nodes_route
