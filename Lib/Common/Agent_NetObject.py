
import networkx as nx
from Lib.Net.NetObj import CNetObj
from  Lib.Common.TreeNode import CTreeNode, CTreeNodeCache
from copy import deepcopy

b_id = id

def_props = { "edge": "", "position": 0, "direction": 1 }

class CAgent_NO( CNetObj ):
    def __init__( self, name="", parent=None, id=None, saveToRedis=True, props=deepcopy(def_props), ext_fields={} ):
        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis, props=props, ext_fields=ext_fields )
        print( b_id( props ), b_id( self.props ), "111" )

    # def propsDict(self): return self.nxGraph.graph if self.nxGraph else {}
