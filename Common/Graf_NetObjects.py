
import networkx as nx
from Net.NetObj import *
from .GuiUtils import GraphEdgeName
from .StrTypeConverter import *

class CGrafRoot_NO( CNetObj ):
    def __init__( self, name="", parent=None, id=None, nxGraf=None ):
        self.nxGraf = nxGraf
        super().__init__( name=name, parent=parent, id=id )

    def propsDict(self): return self.nxGraf.graph

    def onLoadFromRedis( self, redisConn, netObj ):
        super().onLoadFromRedis( redisConn, netObj )
        # при загрузке из сети self.props уже загрузится в коде предка
        self.nxGraf = nx.DiGraph( **self.props )


###################################################################################

class CGrafNode_NO( CNetObj ):
    def ObjPrepareDelete( self, netCmd ):
        incEdges = list( self.nxGraf().out_edges( self.name ) ) +  list( self.nxGraf().in_edges( self.name ) )

        for edgeID in incEdges:
            n1 = edgeID[0]
            n2 = edgeID[1]
            edgeObj = self.resolvePath('../../Edges/' + GraphEdgeName( n1, n2 ) )
            if ( edgeObj ):
                CNetObj_Manager.sendNetCMD( CNetCmd( CNetObj_Manager.clientID, EV.ObjPrepareDelete, Obj_UID = edgeObj.UID ) )

        # при удалении NetObj объекта ноды удаляем соответствующую ноду из графа
        self.nxGraf().remove_node( self.name )

    def propsDict(self): return self.nxNode()

    def onLoadFromRedis( self, redisConn, netObj ):
        super().onLoadFromRedis( redisConn, netObj )
        self.nxGraf().add_node( self.name, **self.props )

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

    def ObjPrepareDelete( self, netCmd ):
        # при удалении NetObj объекта грани удаляем соответствующую грань из графа
        # такой грани уже может не быть в графе, если изначально удалялась нода, она сама внутри графа удалит инцидентную грань
        if self.__has_nxEdge():
            self.nxGraf().remove_edge( *self.__nxEdgeName() )

    def propsDict(self): return self.nxEdge()

    def onLoadFromRedis( self, redisConn, netObj ):
        super().onLoadFromRedis( redisConn, netObj )
        self.nxNodeID_1 = redisConn.get( self.redisKey_NodeID_1() ).decode()
        self.nxNodeID_2 = redisConn.get( self.redisKey_NodeID_2() ).decode()
        self.nxGraf().add_edge( self.nxNodeID_1, self.nxNodeID_2, **self.props )

    def onSaveToRedis( self, redisConn ):
        super().onSaveToRedis( redisConn )
        redisConn.set( self.redisKey_NodeID_1(), self.nxNodeID_1 )
        redisConn.set( self.redisKey_NodeID_2(), self.nxNodeID_2 )

    def __has_nxEdge(self): return self.nxGraf().has_edge( self.nxNodeID_1, self.nxNodeID_2 )
    def __nxEdgeName(self): return ( self.nxNodeID_1, self.nxNodeID_2 )
    def nxGraf(self): return self.grafNode().nxGraf
    def nxEdge(self): return self.nxGraf().edges()[ self.__nxEdgeName() ] if self.__has_nxEdge() else {}
    def grafNode(self): return self.resolvePath('../../')
