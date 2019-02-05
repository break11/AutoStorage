
import networkx as nx
from Net.NetObj import CTreeNode, CNetObj
from .GuiUtils import EdgeDisplayName
import weakref

class CGraphRoot_NO( CNetObj ):
    def __init__( self, name="", parent=None, id=None, saveToRedis=True, nxGraph=None ):
        self.nxGraph = nxGraph
        self.__edges = None
        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis )

    # def ObjPrepareDelete( self, netCmd ):
    #     self.__edges = None

    def propsDict(self): return self.nxGraph.graph if self.nxGraph else {}

    def onLoadFromRedis( self ):
        super().onLoadFromRedis()

        # при загрузке из сети self.props уже загрузится в коде предка
        self.nxGraph = nx.DiGraph( **self.props )

    def edgesNode( self ):
        if self.__edges is None:
            self.__edges = self.childByName( 'Edges')
            if self.__edges: self.__edges = weakref.ref( self.__edges )
        return self.__edges() if self.__edges else None

###################################################################################

class CGraphNode_NO( CNetObj ):
    def __init__( self, name="", parent=None, id=None, saveToRedis=True ):
        self.__graphNode = None
        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis )

    def ObjPrepareDelete( self, netCmd ):
        incEdges = []
        if self.nxGraph():
            incEdges = list( self.nxGraph().out_edges( self.name ) ) +  list( self.nxGraph().in_edges( self.name ) )

        edges = self.graphNode().edgesNode()
        if edges:
            for edgeID in incEdges:
                n1 = edgeID[0]
                n2 = edgeID[1]
                edgeObj = edges.childByName( EdgeDisplayName( n1, n2 ) )
                if ( edgeObj ):
                    edgeObj.localDestroy()

        # при удалении NetObj объекта ноды удаляем соответствующую ноду из графа
        self.nxGraph().remove_node( self.name )
        self.__graphNode = None

    def propsDict(self): return self.nxNode() if self.graphNode() else {}

    def onLoadFromRedis( self ):
        super().onLoadFromRedis()

        # попытка создать объект, которого уже нет в редис
        if self.graphNode():
            self.nxGraph().add_node( self.name, **self.props )

    def nxGraph(self)  : return self.graphNode().nxGraph if self.graphNode() else None
    def nxNode(self)   : return self.nxGraph().nodes()[ self.name ] if self.nxGraph() else {}
    def graphNode(self):
        if self.__graphNode is None:
            self.__graphNode = CTreeNode.resolvePath( self, '../../')
        return self.__graphNode

###################################################################################

class CGraphEdge_NO( CNetObj ):
    __s_NodeID_1 = "NodeID_1"
    __s_NodeID_2 = "NodeID_2"

    def __init__( self, name="", parent=None, id=None, saveToRedis=True, nxNodeID_1=None, nxNodeID_2=None ):
        self.ext_fields = {}
        self.ext_fields[ self.__s_NodeID_1 ] = nxNodeID_1
        self.ext_fields[ self.__s_NodeID_2 ] = nxNodeID_2
        self.__graphNode = None

        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis )

    def ObjPrepareDelete( self, netCmd ):
        # при удалении NetObj объекта грани удаляем соответствующую грань из графа
        # такой грани уже может не быть в графе, если изначально удалялась нода, она сама внутри графа удалит инцидентную грань
        if self.__has_nxEdge():
            self.nxGraph().remove_edge( *self.__nxEdgeName() )
        self.__graphNode = None

    def propsDict(self): return self.nxEdge() if self.graphNode() else {}

    def onLoadFromRedis( self ):
        super().onLoadFromRedis()

        if self.graphNode():
            self.nxGraph().add_edge( self.nxNodeID_1(), self.nxNodeID_2(), **self.props )

    def nxNodeID_1(self)  : return self.ext_fields[ self.__s_NodeID_1 ]
    def nxNodeID_2(self)  : return self.ext_fields[ self.__s_NodeID_2 ]
    def __has_nxEdge(self): return self.nxGraph().has_edge( self.nxNodeID_1(), self.nxNodeID_2() ) if self.nxGraph() else None
    def __nxEdgeName(self): return ( self.nxNodeID_1(), self.nxNodeID_2() )
    def nxGraph(self)     : return self.graphNode().nxGraph if self.graphNode() else None
    def nxEdge(self)      : return self.nxGraph().edges()[ self.__nxEdgeName() ] if self.__has_nxEdge() else {}
    def graphNode(self):
        if self.__graphNode is None:
            self.__graphNode = CTreeNode.resolvePath( self, '../../')
        return self.__graphNode
