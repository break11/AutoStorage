
from Lib.Net.NetObj import CNetObj
# from Lib.Common.TreeNode import CTreeNode, CTreeNodeCache
from Lib.Common.Utils import СStrProps_Meta

class SBoxProps( metaclass = СStrProps_Meta ):
    address = None

SBP = SBoxProps

def_props = { SBP.address: "" }

def boxesNodeCache():
    return CTreeNodeCache( baseNode = CNetObj_Manager.rootObj, path = "Boxes" )

def queryBoxNetObj( name ):
    props = deepcopy( def_props )
    return boxesNodeCache()().queryObj( sName=name, ObjClass=CBox_NO, props=props )

class CBox_NO( CNetObj ):
    @property
    def nxGraph( self ): return self.graphRootNode().nxGraph

    def __init__( self, name="", parent=None, id=None, saveToRedis=True, props=None, ext_fields=None ):
        self.graphRootNode = boxesNodeCache()
        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis, props=props, ext_fields=ext_fields )
