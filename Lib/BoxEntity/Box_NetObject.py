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
from Lib.GraphEntity.Graph_NetObjects import graphNodeCache
from Lib.AgentEntity.Agent_NetObject import agentsNodeCache

s_Boxes = "Boxes"

class SBoxProps( metaclass = СStrProps_Meta ):
    address = None

SBP = SBoxProps


def boxesNodeCache():
    return CTreeNodeCache( baseNode = CNetObj_Manager.rootObj, path = s_Boxes )

def queryBoxNetObj( name ):
    props = deepcopy( CBox_NO.def_props )
    return boxesNodeCache()().queryObj( sName=name, ObjClass=CBox_NO, props=props )

####################

class CBox_NO( CNetObj ):
    def_props = { SBP.address: CBoxAddress( addressType=EBoxAddressType.Undefined ) }

    @property
    def nxGraph( self ): return self.graphRootNode().nxGraph if self.graphRootNode() is not None else None

    def __init__( self, name="", parent=None, id=None, saveToRedis=True, props=None, ext_fields=None ):
        self.graphRootNode = graphNodeCache()
        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis, props=props, ext_fields=ext_fields )

    def ObjPropCreated( self, netCmd ):
        if netCmd.sPropName == SBP.address:
            self.updateAddressCache()

    def ObjPropUpdated( self, netCmd ):
        if netCmd.sPropName == SBP.address:
            self.updateAddressCache()
    
    def ObjPropDeleted( self, netCmd ):
        if netCmd.sPropName == SBP.address:
            sPropName = netCmd.value.data.toString()
            if self.parent.get( sPropName ):
                del self.parent[ sPropName ]

    def ObjCreated( self, netCmd ):
        self.updateAddressCache()

    def ObjPrepareDelete( self, netCmd ):
        propAddress = self.get( SBP.address )
        if propAddress:
            sPropName = propAddress.data.toString()
            if self.parent.get( sPropName ):
                del self.parent[ sPropName ]

    #############

    def updateAddressCache( self ):
        propAddress = self.get( SBP.address )
        if propAddress:
            sPropName = propAddress.data.toString()
            self.parent.local_props.add( sPropName )
            self.parent[ sPropName ] = self.name

    def isValidAddress( self ):
        if self.address.addressType == EBoxAddressType.Undefined:
            return False
        
        if self.address.addressType == EBoxAddressType.OnNode:
            return self.nxGraph.has_node( self.address.data.nodeID ) if self.nxGraph is not None else False

        if self.address.addressType == EBoxAddressType.OnAgent:
            return agentsNodeCache()().childByName( str(self.address.data) ) is not None

####################

def loadBoxes_to_NetObj( sFName, bReload ):
    if not destroy_If_Reload( s_Boxes, bReload ): return False

    if not os.path.exists( sFName ):
        print( f"{SC.sWarning} Boxes file not found '{sFName}'!" )
        return False

    Boxes_NetObj = CNetObj_Manager.rootObj.queryObj( s_Boxes,  CNetObj )
    with open( sFName, "r" ) as read_file:
        Boxes = json.load( read_file )
        nJSON.load_Data( jData=Boxes, parent=Boxes_NetObj, bLoadUID=False )

    return True

