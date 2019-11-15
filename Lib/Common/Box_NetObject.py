import os
import json
from enum import auto

from Lib.Net.NetObj import CNetObj
from Lib.Net.NetObj_Manager import CNetObj_Manager
import Lib.Net.NetObj_JSON as nJSON
from Lib.Net.NetObj_Utils import destroy_If_Reload
from Lib.Common.TreeNode import CTreeNode, CTreeNodeCache
from Lib.Common.StrProps_Meta import СStrProps_Meta
from Lib.Common.StrConsts import SC
from Lib.Common.BaseEnum import BaseEnum
import Lib.Common.StorageGraphTypes as SGT

MDS = "="
TDS = ","

# Undefined = 25,Left,555
# BoxOnNode = 25,Left
# BoxOnAgent = 555

class EBoxAddressType( BaseEnum ):
    Undefined  = auto()
    BoxOnNode  = auto()
    BoxOnAgent = auto()

    Default = Undefined

class CBoxAddress:
    dataFromStrFunc = {
                        EBoxAddressType.Undefined   : lambda sData : sData.split( TDS )[:3:],
                        EBoxAddressType.BoxOnNode   : CBoxAddress.BoxOnNode_fromString,
                        EBoxAddressType.BoxOnAgent  : CBoxAddress.BoxOnAgent_fromString,
                      }
    dataToStrFunc   = {
                        EBoxAddressType.Undefined  : lambda boxAddress : f"{boxAddress.nodeID}{ TDS }{boxAddress.placeSide}{ TDS }{boxAddress.agentN}",
                        EBoxAddressType.BoxOnNode  : lambda boxAddress : f"{boxAddress.nodeID}{ TDS }{boxAddress.placeSide}",
                        EBoxAddressType.BoxOnAgent : lambda boxAddress : f"{boxAddress.agentN}",
                      }

    def __init__( self, addressType, nodeID = None, placeSide = None, agentN = None ):
        self.addressType = addressType

        self.nodeID    = nodeID
        self.placeSide = placeSide
        self.agentN    = agentN

    def __str__( self ): return self.toString()

    @classmethod
    def fromString( cls, data ):
        l = data.split( MDS )
        addressType = ETaskType.fromString( l[0] )
        if len( l ) > 1:
            nodeID, placeSide, agentN = cls.dataFromString( addressType, l[1] )
        else:
            nodeID, placeSide, agentN = None, None, None
        return CBoxAddress( addressType, nodeID=nodeID, placeSide=placeSide, agentN=agentN )

    def toString( self ):
        sR = f"{self.addressType}"
        if any( self.nodeID, self.placeSide, self.agentN ):
            sR = f"{sR}{MDS}{self.dataToString()}"
        return sR

    @classmethod
    def dataFromString( cls, addressType, sData ):
        try:
            return cls.dataFromStrFunc[ addressType ]( sData )
        except:
            return None, None, None

    def dataToString( self ):
        return self.dataToStrFunc[ self.addressType ]( self )

###############

    @classmethod
    def BoxOnNode_fromString(cls, sData):
        l = sData.split( TDS )
        nodeID = l[0]
        placeSide = SGT.ESide.fromString(l[1])
        agentN = None

        return nodeID, placeSide, agentN
    
    @classmethod
    def BoxOnAgent_fromString(cls, sData):
        l = sData.split( TDS )
        nodeID = None
        placeSide = None
        agentN = int(l[0])

        return nodeID, placeSide, agentN
    
###############

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
    def_props = { SBP.address: "" }

    # @property
    # def nxGraph( self ): return self.graphRootNode().nxGraph

    def __init__( self, name="", parent=None, id=None, saveToRedis=True, props=def_props, ext_fields=None ):
        print( boxesNodeCache()(), parent )
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

