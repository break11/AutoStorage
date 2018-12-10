
import networkx as nx
from Net.NetObj import *
from .StorageGrafTypes import *
from .GuiUtils import GraphEdgeName
from .StrTypeConverter import *

def adjustGrafProps( d ):
    d1 = {}
    for k,v in d.items():
        k1 = k.decode() 
        v1 = v.decode()
        d1[ k1 ] = adjustAttrType( k1, v1 )
    return d1


class CGrafRoot_NO( CNetObj ):
    def __init__( self, name="", parent=None, id=None, nxGraf=None ):
        self.nxGraf = nxGraf
        super().__init__( name=name, parent=parent, id=id )

    def propsDict(self): return self.nxGraf.graph

    def onLoadFromRedis( self, redisConn, netObj ):
        super().onLoadFromRedis( redisConn, netObj )
        props = CStrTypeConverter.DictFromBytes( redisConn.hgetall( self.redisKey_Props() ) )
        self.nxGraf = nx.DiGraph( **props )

###################################################################################

class CGrafNode_NO( CNetObj ):
    def propsDict(self): return self.nxNode()

    def onLoadFromRedis( self, redisConn, netObj ):
        super().onLoadFromRedis( redisConn, netObj )
        props = CStrTypeConverter.DictFromBytes( redisConn.hgetall( self.redisKey_Props() ) )
        self.nxGraf().add_node( self.name, **props )

    def nxGraf(self): return self.grafNode().nxGraf
    def nxNode(self): return self.nxGraf().nodes()[ self.name ]
    def grafNode(self): return self.resolvePath('../../')

###################################################################################

class CGrafEdge_NO( CNetObj ):
    __s_NodeID_1 = "NodeID_1"
    __s_NodeID_2 = "NodeID_2"

    def redisKey_NodeID_1(self): return f"{self.redisBase_Name()}:{self.__s_NodeID_1}"
    def redisKey_NodeID_2(self): return f"{self.redisBase_Name()}:{self.__s_NodeID_2}"

    def __init__( self, name="", nxNodeID_1=None, nxNodeID_2=None, parent=None, id=None, nxEdge=None ):
        self.nxNodeID_1 = nxNodeID_1
        self.nxNodeID_2 = nxNodeID_2
        super().__init__( name=name, parent=parent, id=id )

        CNetObj_Manager.addCallback( EV.ObjPrepareDelete, self.OnPrepareDelete )
    
    def OnPrepareDelete(self, netCmd):
        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID, genAssert=True )

        if isinstance( netObj, CGrafNode_NO ):
            if netObj.name in self.__nxEdgeName():
                
                cmd = CNetCmd( CNetObj_Manager.clientID, EV.ObjPrepareDelete, Obj_UID = self.UID )
                CNetObj_Manager.sendNetCMD( cmd )

        if not self.UID == netCmd.Obj_UID: return

        # при удалении NetObj объекта грани удаляем соответствующую грань из графа
        self.nxGraf().remove_edge( *self.__nxEdgeName() )

    def propsDict(self): return self.nxEdge()

    def onLoadFromRedis( self, redisConn, netObj ):
        super().onLoadFromRedis( redisConn, netObj )
        props = CStrTypeConverter.DictFromBytes( redisConn.hgetall( self.redisKey_Props() ) )
        self.nxNodeID_1 = redisConn.get( self.redisKey_NodeID_1() ).decode()
        self.nxNodeID_2 = redisConn.get( self.redisKey_NodeID_2() ).decode()
        self.nxGraf().add_edge( self.nxNodeID_1, self.nxNodeID_2, **props )

    def onSaveToRedis( self, redisConn ):
        super().onSaveToRedis( redisConn )
        redisConn.set( self.redisKey_NodeID_1(), self.nxNodeID_1 )
        redisConn.set( self.redisKey_NodeID_2(), self.nxNodeID_2 )

    def __nxEdgeName(self): return ( self.nxNodeID_1, self.nxNodeID_2 )
    def nxGraf(self): return self.grafNode().nxGraf
    def nxEdge(self): return self.nxGraf().edges()[ self.__nxEdgeName() ]
    def grafNode(self): return self.resolvePath('../../')
