
import networkx as nx
from Lib.Net.NetObj import CNetObj
from  Lib.Common.TreeNode import CTreeNode, CTreeNodeCache
from .GuiUtils import EdgeDisplayName

class CGraphRoot_NO( CNetObj ):
    def __init__( self, name="", parent=None, id=None, saveToRedis=True, props={}, ext_fields={},
                  nxGraph=None ):

        if nxGraph is not None:
            self.nxGraph = nxGraph
        else:
            self.nxGraph = nx.DiGraph( props )

        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis, props=props, ext_fields=ext_fields )

        self.edgesNode = CTreeNodeCache( baseNode = self, path = "Edges" )

    def propsDict(self): return self.nxGraph.graph if self.nxGraph else {}

###################################################################################

class CGraphNode_NO( CNetObj ):
    def __init__( self, name="", parent=None, id=None, saveToRedis=True, props={}, ext_fields={} ):

        self.graphNode = CTreeNodeCache( baseNode = self, path = "../../" )

        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis, props=props, ext_fields=ext_fields )

        if self.graphNode():
            self.nxGraph().add_node( self.name, **self.props )

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
        if self.__has_nxNode():
            self.nxGraph().remove_node( self.name )

    def propsDict(self): return self.nxNode() if self.graphNode() else {}

    def nxGraph(self)     : return self.graphNode().nxGraph if self.graphNode() else None
    def nxNode(self)      : return self.nxGraph().nodes()[ self.name ] if self.nxGraph() else {}
    def __has_nxNode(self): return self.nxGraph().has_node( self.name ) if self.nxGraph() else None

###################################################################################

class CGraphEdge_NO( CNetObj ):
    s_NodeID_1 = "NodeID_1"
    s_NodeID_2 = "NodeID_2"

    def __init__( self, name="", parent=None, id=None, saveToRedis=True, props={}, ext_fields={} ):

        self.graphNode = CTreeNodeCache( baseNode = self, path = "../../" )

        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis, props=props, ext_fields=ext_fields )

        if self.graphNode():
            self.nxGraph().add_edge( self.nxNodeID_1(), self.nxNodeID_2(), **self.props )

    def ObjPrepareDelete( self, netCmd ):
        # при удалении NetObj объекта грани удаляем соответствующую грань из графа
        # такой грани уже может не быть в графе, если изначально удалялась нода, она сама внутри графа удалит инцидентную грань
        if self.__has_nxEdge():
            self.nxGraph().remove_edge( *self.__nxEdgeName() )

    def propsDict(self): return self.nxEdge() if self.graphNode() else {}

    def nxNodeID_1(self)  : return self.ext_fields[ self.s_NodeID_1 ]
    def nxNodeID_2(self)  : return self.ext_fields[ self.s_NodeID_2 ]
    def __has_nxEdge(self): return self.nxGraph().has_edge( self.nxNodeID_1(), self.nxNodeID_2() ) if self.nxGraph() else None
    def __nxEdgeName(self): return ( self.nxNodeID_1(), self.nxNodeID_2() )
    def nxGraph(self)     : return self.graphNode().nxGraph if self.graphNode() else None
    def nxEdge(self)      : return self.nxGraph().edges()[ self.__nxEdgeName() ] if self.__has_nxEdge() else {}
