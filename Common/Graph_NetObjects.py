
import networkx as nx
from Net.NetObj import *
from .GuiUtils import GraphEdgeName
from .StrTypeConverter import *

class CGraphRoot_NO( CNetObj ):
    def __init__( self, name="", parent=None, id=None, nxGraph=None ):
        self.nxGraph = nxGraph
        super().__init__( name=name, parent=parent, id=id )

    def propsDict(self): return self.nxGraph.graph if self.nxGraph else {}
        # return self.nxGraph.graph

    def onLoadFromRedis( self, redisConn, netObj ):
        super().onLoadFromRedis( redisConn, netObj )
        # при загрузке из сети self.props уже загрузится в коде предка
        self.nxGraph = nx.DiGraph( **self.props )


###################################################################################

class CGraphNode_NO( CNetObj ):
    def ObjPrepareDelete( self, netCmd ):
        incEdges = list( self.nxGraph().out_edges( self.name ) ) +  list( self.nxGraph().in_edges( self.name ) )

        for edgeID in incEdges:
            n1 = edgeID[0]
            n2 = edgeID[1]
            edgeObj = self.resolvePath('../../Edges/' + GraphEdgeName( n1, n2 ) )
            if ( edgeObj ):
                CNetObj_Manager.sendNetCMD( CNetCmd( Event=EV.ObjPrepareDelete, Obj_UID = edgeObj.UID ) )

        # при удалении NetObj объекта ноды удаляем соответствующую ноду из графа
        self.nxGraph().remove_node( self.name )

    def propsDict(self): return self.nxNode() if self.graphNode() else {}
        # return self.nxNode()

    def onLoadFromRedis( self, redisConn, netObj ):
        super().onLoadFromRedis( redisConn, netObj )
        self.nxGraph().add_node( self.name, **self.props )

    def nxGraph(self): return self.graphNode().nxGraph
    def nxNode(self): return self.nxGraph().nodes()[ self.name ]
    def graphNode(self): return self.resolvePath('../../')

###################################################################################

class CGraphEdge_NO( CNetObj ):
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
            self.nxGraph().remove_edge( *self.__nxEdgeName() )

    def propsDict(self): return self.nxEdge() if self.graphNode() else {}
        #  return self.nxEdge()

    def onLoadFromRedis( self, redisConn, netObj ):
        super().onLoadFromRedis( redisConn, netObj )

        pipe = redisConn.pipeline()
        pipe.get( self.redisKey_NodeID_1() )
        pipe.get( self.redisKey_NodeID_2() )
        values = pipe.execute()

        # попытка создать объект, которого уже нет в редис
        if values[0] is None: return

        self.nxNodeID_1 = values[0].decode()
        self.nxNodeID_2 = values[1].decode()

        if self.graphNode():
            self.nxGraph().add_edge( self.nxNodeID_1, self.nxNodeID_2, **self.props )

    def onSaveToRedis( self, redisConn ):
        super().onSaveToRedis( redisConn )

        pipe = redisConn.pipeline()

        pipe.set( self.redisKey_NodeID_1(), self.nxNodeID_1 )
        pipe.set( self.redisKey_NodeID_2(), self.nxNodeID_2 )

        pipe.execute()

    def __has_nxEdge(self): return self.nxGraph().has_edge( self.nxNodeID_1, self.nxNodeID_2 )
    def __nxEdgeName(self): return ( self.nxNodeID_1, self.nxNodeID_2 )
    def nxGraph(self): return self.graphNode().nxGraph
    def nxEdge(self): return self.nxGraph().edges()[ self.__nxEdgeName() ] if self.__has_nxEdge() else {}
    def graphNode(self): return self.resolvePath('../../')
