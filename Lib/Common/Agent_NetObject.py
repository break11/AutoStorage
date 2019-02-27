
import networkx as nx
from Lib.Net.NetObj import CNetObj
from  Lib.Common.TreeNode import CTreeNode, CTreeNodeCache
from .GuiUtils import EdgeDisplayName

class CAgent_NO( CNetObj ):
    def __init__( self, name="", parent=None, id=None, saveToRedis=True ):
        self.props = { "edge": "", "position": 0 }
        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis )

    def onLoadFromRedis( self ):
        super().onLoadFromRedis()
