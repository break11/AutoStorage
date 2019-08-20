
import networkx as nx
from copy import deepcopy
from collections import namedtuple

from Lib.Net.NetObj import CNetObj
from Lib.Common.TreeNode import CTreeNode, CTreeNodeCache
from Lib.Net.NetObj_Manager import CNetObj_Manager
import Lib.Common.GraphUtils as GU
from Lib.Common.Graph_NetObjects import graphNodeCache
from Lib.AgentProtocol.AgentDataTypes import EAgent_Status, blockAutoControlStatuses, EAgent_CMD_State
from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event as EV
from Lib.Common import StorageGraphTypes as SGT
from Lib.Common.Utils import СStrProps_Meta

class SAgentProps( metaclass = СStrProps_Meta ):
    edge          = None
    position      = None
    route         = None
    route_idx     = None
    angle         = None
    odometer      = None
    status        = None
    charge        = None
    auto_control  = None
    connectedTime = None
    cmd_PE        = None
    cmd_PD        = None
    cmd_BR        = None
    cmd_ES        = None
    cmd_BL_L      = None
    cmd_BL_R      = None
    cmd_BU_L      = None
    cmd_BU_R      = None
    cmd_BA        = None
    RTele         = None

SAP = SAgentProps

cmdDesc = namedtuple( "cmdDesc", "event data" )

cmdProps = { SAP.cmd_PE   : cmdDesc( event=EV.PowerEnable,    data=None),
             SAP.cmd_PD   : cmdDesc( event=EV.PowerDisable,   data=None),
             SAP.cmd_BR   : cmdDesc( event=EV.BrakeRelease,   data=None),
             SAP.cmd_ES   : cmdDesc( event=EV.EmergencyStop,  data=None),
             SAP.cmd_BL_L : cmdDesc( event=EV.BoxLoad,        data=SGT.ESide.Left.toChar()  ),
             SAP.cmd_BL_R : cmdDesc( event=EV.BoxLoad,        data=SGT.ESide.Right.toChar() ),
             SAP.cmd_BU_L : cmdDesc( event=EV.BoxUnload,      data=SGT.ESide.Left.toChar()  ),
             SAP.cmd_BU_R : cmdDesc( event=EV.BoxUnload,      data=SGT.ESide.Right.toChar() ),
             SAP.cmd_BA   : cmdDesc( event=EV.BoxLoadAborted, data=None),
            }

cmdDesc_To_Prop = {} #type:ignore
for k, v in cmdProps.items():
    cmdDesc_To_Prop[ v ] = k

cmdProps_keys = cmdProps.keys()

def_props = { SAP.status: EAgent_Status.Idle, SAP.edge: "", SAP.position: 0, SAP.route: "", SAP.route_idx: 0,
              SAP.angle : 0.0, SAP.odometer : 0, SAP.charge : 0, SAP.connectedTime : 0, SAP.auto_control : 1,

              SAP.cmd_PE   : EAgent_CMD_State.Done, SAP.cmd_PD   : EAgent_CMD_State.Done,
              SAP.cmd_BR   : EAgent_CMD_State.Done, SAP.cmd_ES   : EAgent_CMD_State.Done,
              SAP.cmd_BL_L : EAgent_CMD_State.Done, SAP.cmd_BL_R : EAgent_CMD_State.Done,
              SAP.cmd_BU_L : EAgent_CMD_State.Done, SAP.cmd_BU_R : EAgent_CMD_State.Done,
              SAP.cmd_BA   : EAgent_CMD_State.Done,

              SAP.RTele : 1 }

def agentsNodeCache():
    return CTreeNodeCache( baseNode = CNetObj_Manager.rootObj, path = "Agents" )

def queryAgentNetObj( name ):
    props = deepcopy( def_props )
    return agentsNodeCache()().queryObj( sName=name, ObjClass=CAgent_NO, props=props )

class CAgent_NO( CNetObj ):
    @property
    def nxGraph( self ): return self.graphRootNode().nxGraph

    def __init__( self, name="", parent=None, id=None, saveToRedis=True, props=None, ext_fields=None ):
        self.graphRootNode = graphNodeCache()
        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis, props=props, ext_fields=ext_fields )

    def ObjPropUpdated( self, netCmd ):
        if netCmd.sPropName == SAP.status:
            if netCmd.value in blockAutoControlStatuses:
                self.auto_control = 0

    # def propsDict(self): return self.nxGraph.graph if self.nxGraph else {}
    def isOnTrack( self ):
        if ( not self.edge ) or ( not self.graphRootNode() ):
            return

        tEdgeKey = GU.tEdgeKeyFromStr(self.edge)

        if len(tEdgeKey) < 2 :
            return
        
        nodeID_1 = tEdgeKey[0]
        nodeID_2 = tEdgeKey[1]

        if not self.nxGraph.has_edge( nodeID_1, nodeID_2 ):
            return
        
        return tEdgeKey

    def isOnNode( self, nodeType = None ):
        tEdgeKey = self.isOnTrack
        if not tEdgeKey: return False

        return True if (nodeType is None) else GU.isOnNode( self.nxGraph, nodeType, tEdgeKey, self.position )

    
    def putToNode( self, nodeID ):        
        if not self.nxGraph.has_node( nodeID ): return

        if GU.nodeType( self.nxGraph, nodeID ) == SGT.ENodeTypes.Terminal: return

        edges = list( self.nxGraph.out_edges( nodeID ) ) + list( self.nxGraph.in_edges( nodeID ) )
        if len( edges ) == 0: return

        tEdgeKey = edges[ 0 ]
        self.edge = GU.tEdgeKeyToStr( tEdgeKey )
        self.position = 0 if tEdgeKey[ 0 ] == nodeID else GU.edgeSize( self.nxGraph, tEdgeKey )

    def goToNode( self, targetNode ):
        if not self.nxGraph.has_node( targetNode ): return

        tKey = self.isOnTrack()
        if tKey is None:
            self.putToNode( targetNode )
            return

        startNode = tKey[0]

        if GU.nodeType( self.nxGraph, targetNode ) == SGT.ENodeTypes.Terminal: return

        nodes_route = nx.algorithms.dijkstra_path(self.nxGraph, startNode, targetNode)
        self.applyRoute( nodes_route )

    def goToCharge(self):
        tEdgeKey = self.isOnTrack()
        if tEdgeKey is None: return
        startNode = tEdgeKey[0]

        route_weight, nodes_route = GU.routeToServiceStation( self.nxGraph, startNode, self.angle )
        if len(nodes_route) == 0:
            self.status = EAgent_Status.NoRouteToCharge
            print(f"{SC.sError} Cant find any route to service station.")
        else:
            self.status = EAgent_Status.GoToCharge

        self.applyRoute( nodes_route )


    def applyRoute( self, nodes_route ): #TODO юнит-тест
        tKey = self.isOnTrack()
        assert tKey is not None

        if len(nodes_route) < 2: return

        curEdgeSize = GU.edgeSize( self.nxGraph, tKey )

        # перепрыгивание на кратную грань, если челнок стоит на грани противоположной направлению маршрута
        if ( nodes_route[0], nodes_route[1] ) != tKey:
            tKey = tuple( reversed(tKey) )
            self.edge = GU.tEdgeKeyToStr( tKey )
            curEdgeSize = GU.edgeSize( self.nxGraph, tKey )
            self.position = curEdgeSize - self.position
            if nodes_route[0] != tKey[0]:
                nodes_route.insert(0, tKey[0] )
        
        if ( self.position / curEdgeSize ) > 0.5:
            if len( nodes_route ) > 2:
                nodes_route = nodes_route[1:]
                tKey = ( nodes_route[0], nodes_route[1] )
                self.edge = GU.tEdgeKeyToStr( tKey )
                self.position = 0
            else:
                return

        self.route = ",".join( nodes_route )




