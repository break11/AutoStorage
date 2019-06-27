
import networkx as nx
from copy import deepcopy

from Lib.Net.NetObj import CNetObj
from Lib.Common.TreeNode import CTreeNode, CTreeNodeCache
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Common.GraphUtils import tEdgeKeyFromStr
from Lib.Common.Graph_NetObjects import graphNodeCache

from enum import IntEnum, auto
from .Utils import EnumFromString

class EAgent_Status( IntEnum ):
    Idle              = auto()
    PositionSyncError = auto()
    GoToCharge        = auto()
    Charging          = auto()

    @staticmethod
    def fromString( sType ): return EnumFromString( EAgent_Status, sType, EAgent_Status.Idle )

s_edge      = "edge"
s_position  = "position"
s_route     = "route"
s_route_idx = "route_idx"
s_angle     = "angle"
s_odometer  = "odometer"
s_status    = "status"

def_props = { s_status: EAgent_Status.Idle.name, s_edge: "", s_position: 0, s_route: "", s_route_idx: 0, s_angle : 0, s_odometer : 0 }

def agentsNodeCache():
    return CTreeNodeCache( baseNode = CNetObj_Manager.rootObj, path = "Agents" )

def queryAgentNetObj( name ):
    props = deepcopy( def_props )
    return agentsNodeCache()().queryObj( sName=name, ObjClass=CAgent_NO, props=props )

class CAgent_NO( CNetObj ):    
    def __init__( self, name="", parent=None, id=None, saveToRedis=True, props=None, ext_fields=None ):
        self.graphRootNode = graphNodeCache()
        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis, props=props, ext_fields=ext_fields )

    # def propsDict(self): return self.nxGraph.graph if self.nxGraph else {}
    def isOnTrack( self ):
        if ( not self.edge ) or ( not self.graphRootNode() ):
            return

        tEdgeKey = tEdgeKeyFromStr(self.edge)

        if len(tEdgeKey) < 2 :
            return
        
        nodeID_1 = tEdgeKey[0]
        nodeID_2 = tEdgeKey[1]

        nxGraph = self.graphRootNode().nxGraph
        if not nxGraph.has_edge( nodeID_1, nodeID_2 ):
            return
        
        return tEdgeKey