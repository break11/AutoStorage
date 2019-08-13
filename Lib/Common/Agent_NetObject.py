
import networkx as nx
from copy import deepcopy

from Lib.Net.NetObj import CNetObj
from Lib.Common.TreeNode import CTreeNode, CTreeNodeCache
from Lib.Net.NetObj_Manager import CNetObj_Manager
import Lib.Common.GraphUtils as GU
from Lib.Common.Graph_NetObjects import graphNodeCache
from Lib.AgentProtocol.AgentDataTypes import EAgent_Status

s_edge      = "edge"
s_position  = "position"
s_route     = "route"
s_route_idx = "route_idx"
s_angle     = "angle"
s_odometer  = "odometer"
s_status    = "status"
s_charge    = "charge"
s_connectedTime = "connectedTime"

def_props = { s_status: EAgent_Status.Idle, s_edge: "", s_position: 0, s_route: "", s_route_idx: 0,
              s_angle : 0.0, s_odometer : 0, s_charge : 0, s_connectedTime : 0 }

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

    def isOnNode( self, nodeType ):
        if not self.isOnTrack: return False
    
    def putToNode( self, nodeID ):        
        if not self.nxGraph.has_node( nodeID ): return

        edges = list( self.nxGraph.out_edges( nodeID ) ) + list( self.nxGraph.in_edges( nodeID ) )
        if len( edges ) == 0: return

        tEdgeKey = edges[ 0 ]
        self.edge = GU.tEdgeKeyToStr( tEdgeKey )
        self.position = 0 if tEdgeKey[ 0 ] == nodeID else GU.edgeSize( self.nxGraph, tEdgeKey )



