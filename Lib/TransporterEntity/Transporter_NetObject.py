from copy import deepcopy
import networkx as nx
import os
import json

from Lib.Net.NetObj import CNetObj
# from Lib.Common.TreeNode import CTreeNode,
from Lib.Common.TreeNodeCache import CTreeNodeCache
from Lib.Net.NetObj_Manager import CNetObj_Manager
import Lib.Net.NetObj_JSON as nJSON
# import Lib.Common.GraphUtils as GU
from Lib.GraphEntity.Graph_NetObjects import graphNodeCache
# from Lib.AgentEntity.AgentServer_Event import EAgentServer_Event as EV
# import Lib.AgentEntity.AgentDataTypes as ADT
# import Lib.AgentEntity.AgentTaskData as ATD
# from Lib.GraphEntity import StorageGraphTypes as SGT
from Lib.Common.StrProps_Meta import СStrProps_Meta
import Lib.TransporterEntity.TransporterDataTypes as TDT
from Lib.Common.StrConsts import SC
from Lib.Common.SerializedList import CStrList

s_Transporters = "Transporters"

transportersNodeCache = CTreeNodeCache( path = s_Transporters )

class STransporterProps( metaclass = СStrProps_Meta ):
    busy = None
    mode = None
    masterAddress     = None
    connectionType    = None
    connectionAddress = None
    nodesList = None

STP = STransporterProps

def queryTransporterNetObj( name ):
    props = deepcopy( CTransporter_NO.def_props )
    return transportersNodeCache().queryObj( sName=name, ObjClass=CTransporter_NO, props=props )

class CTransporter_NO( CNetObj ):
    def_props = {
                STP.busy : False,
                STP.mode : TDT.ETransporterMode.Default,
                STP.masterAddress     : SC.localhost,
                STP.connectionType    : TDT.ETransporterConnectionType.Default,
                STP.connectionAddress : f"{SC.localhost}:5020",
                STP.nodesList         : CStrList()
                }
              
    @property
    def nxGraph( self ): return graphNodeCache().nxGraph if graphNodeCache() is not None else None

    def __init__( self, name="", parent=None, id=None, saveToRedis=True, props=None, ext_fields=None ):
        self.lastConnectedTime = 0

        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis, props=props, ext_fields=ext_fields )

####################

def loadTransporters_to_NetObj( sFName ):
    transportersNodeCache().destroyChildren()

    if not os.path.exists( sFName ):
        print( f"{SC.sWarning} Transporters file not found '{sFName}'!" )
        return False

    TS_NetObj = CNetObj_Manager.rootObj.queryObj( s_Transporters, CNetObj )
    with open( sFName, "r" ) as read_file:
        Transporters = json.load( read_file )
        nJSON.load_Data( jData=Transporters, parent=TS_NetObj, bLoadUID=False )

    return True

