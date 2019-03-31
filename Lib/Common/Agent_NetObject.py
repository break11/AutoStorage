
import networkx as nx
from Lib.Net.NetObj import CNetObj
from Lib.Common.TreeNode import CTreeNode, CTreeNodeCache
from copy import deepcopy
from Lib.Net.NetObj_Manager import CNetObj_Manager

b_id = id

s_edge      = "edge"
s_position  = "position"
s_direction = "direction"
s_route     = "route"
s_angle     = "angle"

def_props = { s_edge: "", s_position: 0, s_direction: 1, s_route: "", s_angle: "1,0" }

class CAgent_NO( CNetObj ):
    @property
    def route(self): return self[ s_route ]
    @route.setter
    def route(self, val): self[ s_route ] = val

    @property
    def edge(self): return self[ s_edge ]
    @edge.setter
    def edge(self, val): self[ s_edge ] = val
    
    @property
    def position(self): return self[ s_position ]
    @position.setter
    def position(self, val): self[ s_position ] = val

    @property
    def direction(self): return self[ s_direction ]
    @direction.setter
    def direction(self, val): self[ s_direction ] = val

    @property
    def angle(self): return self[ s_angle ]
    @angle.setter
    def angle(self, val): self[ s_angle ] = val
    
    def __init__( self, name="", parent=None, id=None, saveToRedis=True, props=None, ext_fields=None ):
        self.graphRootNode = CTreeNodeCache( baseNode = CNetObj_Manager.rootObj, path = "Graph" )
        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis, props=props, ext_fields=ext_fields )

    # def propsDict(self): return self.nxGraph.graph if self.nxGraph else {}
    def isOnTrack( self ):
        if ( not self.edge ) or ( not self.graphRootNode() ):
            return

        try:
            tEdgeKey = eval( self.edge )
        except Exception:
            return

        if type(tEdgeKey) is not tuple:
            return
        
        nodeID_1 = str(tEdgeKey[0])
        nodeID_2 = str(tEdgeKey[1])

        nxGraph = self.graphRootNode().nxGraph
        if not nxGraph.has_edge( nodeID_1, nodeID_2 ):
            return
        
        return tEdgeKey

