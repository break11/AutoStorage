import os
import json

from Lib.Net.NetObj import CNetObj
from Lib.Net.NetObj_Manager import CNetObj_Manager
import Lib.Net.NetObj_JSON as nJSON
from Lib.Net.NetObj_Utils import destroy_If_Reload
from Lib.Common.TreeNode import CTreeNodeCache
from Lib.Common.StrProps_Meta import СStrProps_Meta
from Lib.Common.StrConsts import SC
from Lib.BoxEntity.BoxAddress import CBoxAddress, EBoxAddressType

s_Boxes = "Boxes"

class SBoxProps( metaclass = СStrProps_Meta ):
    address = None

SBP = SBoxProps


def boxesNodeCache():
    return CTreeNodeCache( baseNode = CNetObj_Manager.rootObj, path = s_Boxes )

def queryBoxNetObj( name ):
    props = deepcopy( CBox_NO.def_props )
    return boxesNodeCache()().queryObj( sName=name, ObjClass=CBox_NO, props=props )

class CBox_NO( CNetObj ):
    def_props = { SBP.address: CBoxAddress( addressType=EBoxAddressType.Undefined ) }

    # @property
    # def nxGraph( self ): return self.graphRootNode().nxGraph

    def __init__( self, name="", parent=None, id=None, saveToRedis=True, props=def_props, ext_fields=None ):
        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis, props=props, ext_fields=ext_fields )


def loadBoxes_to_NetObj( sFName, bReload ):
    if not destroy_If_Reload( s_Boxes, bReload ): return False

    if not os.path.exists( sFName ):
        print( f"{SC.sWarning} Boxes file not found '{sFName}'!" )
        return False

    Boxes_NetObj = CNetObj_Manager.rootObj.queryObj( s_Boxes,  CNetObj )
    with open( sFName, "r" ) as read_file:
        Boxes = json.load( read_file )
        nJSON.load_Obj_Children( jData=Boxes, obj=Boxes_NetObj )

    # CNetObj(name=s_Boxes, parent=CNetObj_Manager.rootObj)
    # for boxProps in Boxes[ s_Boxes ]:
    #     CBox_NO( parent = boxesNodeCache()(), name = boxProps[  ] )

    return True

