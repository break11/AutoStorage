
import networkx as nx
from Lib.Net.NetObj import CNetObj
from  Lib.Common.TreeNode import CTreeNode, CTreeNodeCache
from .GuiUtils import EdgeDisplayName

class CAgent_NO( CNetObj ):
    def __init__( self, name="", parent=None, id=None, saveToRedis=True, props={}, ext_fields={} ):
        props = { "edge": "", "position": 0, "direction": 1 }
        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis, props=props, ext_fields=ext_fields )
