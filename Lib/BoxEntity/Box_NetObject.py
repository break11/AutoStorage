import os
import json

from Lib.Net.NetObj import CNetObj
from Lib.Net.NetObj_Manager import CNetObj_Manager
import Lib.Net.NetObj_JSON as nJSON
from Lib.Net.NetObj_Utils import isSelfEvent
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Common.TreeNodeCache import CTreeNodeCache
from Lib.Common.StrProps_Meta import СStrProps_Meta
from Lib.Common.StrConsts import SC
from Lib.BoxEntity.BoxAddress import CBoxAddress, EBoxAddressType
from Lib.GraphEntity.Graph_NetObjects import graphNodeCache
from Lib.AgentEntity.Agent_NetObject import agentsNodeCache

s_Boxes = "Boxes"

boxesNodeCache = CTreeNodeCache( path = s_Boxes )

class SBoxProps( metaclass = СStrProps_Meta ):
    address = None

SBP = SBoxProps

def getBox_by_Name( boxName ):
    return boxesNodeCache().childByName( boxName )

def getBox_from_NodePlace( nodePlace ):
    if boxesNodeCache() is None: return None
    boxName = boxesNodeCache().get( str( nodePlace ) )
    return boxesNodeCache().childByName( boxName )

def getBox_by_BoxAddress( boxAddress ):
    if boxesNodeCache() is None: return None
    boxName =  boxesNodeCache().get( str( boxAddress.data ) )
    return getBox_by_Name( boxName )

def queryBoxNetObj( name ):
    props = deepcopy( CBox_NO.def_props )
    return boxesNodeCache().queryObj( sName=name, ObjClass=CBox_NO, props=props )

####################

class CBox_NO( CNetObj ):
    def_props = { SBP.address: CBoxAddress( _type=EBoxAddressType.Undefined ) }

    @property
    def nxGraph( self ): return graphNodeCache().nxGraph if graphNodeCache() is not None else None

    def __init__( self, name="", parent=None, id=None, saveToRedis=True, props=None, ext_fields=None ):
        l = [ EV.ObjCreated, EV.ObjPrepareDelete, EV.ObjCreated.ObjPropCreated, EV.ObjPropUpdated, EV.ObjPropDeleted ]
        for e in l:
            CNetObj_Manager.addCallback( e, self )

        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis, props=props, ext_fields=ext_fields )

    #############
    def ObjPropCreated( self, netCmd ):
        if not isSelfEvent( netCmd, self ): return

        if netCmd.sPropName == SBP.address:
            self.addCacheItem()

    def ObjPropUpdated( self, netCmd ):
        if not isSelfEvent( netCmd, self ): return

        if netCmd.sPropName == SBP.address:
            self.delCacheItem( str(netCmd.oldValue.data) )
            self.addCacheItem()
    
    def ObjPropDeleted( self, netCmd ):
        if not isSelfEvent( netCmd, self ): return

        if netCmd.sPropName == SBP.address:
            self.delCacheItem( str(netCmd.value.data) )

    def ObjCreated( self, netCmd ):
        if not isSelfEvent( netCmd, self ): return

        self.addCacheItem()

    def ObjPrepareDelete( self, netCmd ):
        if not isSelfEvent( netCmd, self ): return

        propAddress = self.get( SBP.address )
        if propAddress:
            self.delCacheItem( str(propAddress.data) )

    def delCacheItem( self, sPropName ):
        boxName = self.parent.get( sPropName )
        if ( boxName is not None ) and ( boxName == self.name ):
            del self.parent[ sPropName ]

    def addCacheItem( self ):
        propAddress = self.get( SBP.address )
        if propAddress:
            sPropName = str(propAddress.data)
            self.parent.local_props.add( sPropName )
            self.parent[ sPropName ] = self.name

    #############

    def isValidAddress( self ):
        if self.address._type == EBoxAddressType.Undefined:
            return False
        
        if self.address._type == EBoxAddressType.OnNode:
            return self.nxGraph.has_node( self.address.data.nodeID ) if self.nxGraph is not None else False

        if self.address._type == EBoxAddressType.OnEdge:
            return self.nxGraph.has_edge( self.address.data.nodeID_1, self.address.data.nodeID_2 ) if self.nxGraph is not None else False

        if self.address._type == EBoxAddressType.OnAgent:
            return agentsNodeCache().childByName( str(self.address.data) ) is not None

####################

def loadBoxes_to_NetObj( sFName ):
    if boxesNodeCache() is not None:
        boxesNodeCache().destroyChildren()

    if not os.path.exists( sFName ):
        print( f"{SC.sWarning} Boxes file not found '{sFName}'!" )
        return False

    Boxes_NetObj = CNetObj_Manager.rootObj.queryObj( s_Boxes,  CNetObj )
    with open( sFName, "r" ) as read_file:
        Boxes = json.load( read_file )
        nJSON.load_Data( jData=Boxes, parent=Boxes_NetObj, bLoadUID=False )

    return True

