from copy import deepcopy
import networkx as nx
import os
import json

from Lib.Net.NetObj import CNetObj
import Lib.Common.BaseTypes as BT
from Lib.Common.TreeNodeCache import CTreeNodeCache
from Lib.Net.NetObj_Manager import CNetObj_Manager
import Lib.Net.NetObj_JSON as nJSON
from Lib.GraphEntity.Graph_NetObjects import graphNodeCache
from Lib.Common.StrProps_Meta import СStrProps_Meta
import Lib.TransporterEntity.TransporterDataTypes as TDT
from Lib.Common.StrConsts import SC
import Lib.Common.BaseTypes as BT
from Lib.Common.SerializedList import CStrList

s_Transporters = "Transporters"

transportersNodeCache = CTreeNodeCache( path = s_Transporters )

class CTransporterRoot_NO( CNetObj ): # пока заглкшка для навешивания контроллеров
    pass

#######################################

class STransporterProps( metaclass = СStrProps_Meta ):
    busy = None
    mode = None
    masterAddress     = None
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
                STP.connectionAddress : BT.CConnectionAddress.TCP_IP( SC.localhost, 5020 ),
                STP.nodesList         : CStrList()
                }
              
    @property
    def nxGraph( self ): return graphNodeCache().nxGraph if graphNodeCache() is not None else None

    def __init__( self, name="", parent=None, id=None, saveToRedis=True, props=None, ext_fields=None ):
        self.lastConnectedTime = 0

        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis, props=props, ext_fields=ext_fields )

####################

def loadTransporters_to_NetObj( sFName ):
    if transportersNodeCache() is not None:
        transportersNodeCache().destroyChildren()

    if not os.path.exists( sFName ):
        print( f"{SC.sWarning} Transporters file not found '{sFName}'!" )
        return False

    TS_NetObj = CNetObj_Manager.rootObj.queryObj( s_Transporters, CTransporterRoot_NO )
    with open( sFName, "r" ) as read_file:
        Transporters = json.load( read_file )
        nJSON.load_Data( jData=Transporters, parent=TS_NetObj, bLoadUID=False )

    return True

