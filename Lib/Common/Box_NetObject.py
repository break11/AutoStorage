import json
import os

from Lib.Net.NetObj import CNetObj
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Common.TreeNode import CTreeNode, CTreeNodeCache
from Lib.Common.StrProps_Meta import СStrProps_Meta
from Lib.Common.StrConsts import SC

s_Boxes = "Boxes"

class SBoxProps( metaclass = СStrProps_Meta ):
    address = None

SBP = SBoxProps

def_props = { SBP.address: "" }

def boxesNodeCache():
    return CTreeNodeCache( baseNode = CNetObj_Manager.rootObj, path = s_Boxes )

def queryBoxNetObj( name ):
    props = deepcopy( def_props )
    return boxesNodeCache()().queryObj( sName=name, ObjClass=CBox_NO, props=props )

class CBox_NO( CNetObj ):
    # @property
    # def nxGraph( self ): return self.graphRootNode().nxGraph

    def __init__( self, name="", parent=None, id=None, saveToRedis=True, props=None, ext_fields=None ):
        # self.boxRootNode = boxesNodeCache()
        print( boxesNodeCache()(), parent )
        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis, props=props, ext_fields=ext_fields )

def loadBoxes_to_NetObj( sFName, bReload ):
    boxesObj = CTreeNode.resolvePath( CNetObj_Manager.rootObj, s_Boxes)
    if boxesObj:
        if bReload:
            boxesObj.destroy()
        else:
            return False

    del boxesObj

    if not os.path.exists( sFName ):
        print( f"{SC.sWarning} Boxes file not found '{sFName}'!" )
        return False

    with open( sFName, "r" ) as read_file:
        Boxes = json.load( read_file )

    CNetObj(name=s_Boxes, parent=CNetObj_Manager.rootObj)
    for boxProps in Boxes[ s_Boxes ]:
        CBox_NO( parent = boxesNodeCache()(), name = boxProps[ SC.UID ] )

    return True

