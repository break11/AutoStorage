
import networkx as nx
from Lib.Net.NetObj import CNetObj
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Common.TreeNode import CTreeNode, CTreeNodeCache
from .GraphUtils import EdgeDisplayName, loadGraphML_File

class CGraphRoot_NO( CNetObj ):
    def __init__( self, name="", parent=None, id=None, saveToRedis=True, props={}, ext_fields={},
                  nxGraph=None ):

        if nxGraph is not None:
            self.nxGraph = nxGraph
        else:
            self.nxGraph = nx.DiGraph( **props )

        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis, props=props, ext_fields=ext_fields )        

        self.nodesNode = CTreeNodeCache( baseNode = self, path = "Nodes" )
        self.edgesNode = CTreeNodeCache( baseNode = self, path = "Edges" )
    
    def propsDict(self): return self.nxGraph.graph if self.nxGraph else {}

###################################################################################

class CGraphNode_NO( CNetObj ):

    def __init__( self, name="", parent=None, id=None, saveToRedis=True, props={}, ext_fields={} ):
        self.graphNode = CTreeNodeCache( baseNode = self, path = "../../" )

        # функция для вызова в конструкторе предка, так как нода nx-графа должна быть заполнена до ObjCreated
        def addNxNode(netObj):
            if not netObj.__has_nxNode():
                netObj.nxGraph().add_node( netObj.name, **netObj.props )

        self._CNetObj__beforeObjCreatedCallback = addNxNode

        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis, props=props, ext_fields=ext_fields )

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
    def nxNode(self)      : return self.nxGraph().nodes()[ self.name ] if self.__has_nxNode() else {}
    def __has_nxNode(self): return self.nxGraph().has_node( self.name ) if self.nxGraph() else None

###################################################################################

class CGraphEdge_NO( CNetObj ):
    s_NodeID_1 = "NodeID_1"
    s_NodeID_2 = "NodeID_2"

    def __init__( self, name="", parent=None, id=None, saveToRedis=True, props={}, ext_fields={} ):

        self.graphNode = CTreeNodeCache( baseNode = self, path = "../../" )

        def addNxEdge(netObj):
            if not netObj.__has_nxEdge():
                netObj.nxGraph().add_edge( netObj.nxNodeID_1(), netObj.nxNodeID_2(), **netObj.props )

        self._CNetObj__beforeObjCreatedCallback = addNxEdge

        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis, props=props, ext_fields=ext_fields )

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

def createGraph_NO_Branches( nxGraph ):
    Graph  = CGraphRoot_NO( name="Graph", parent=CNetObj_Manager.rootObj, nxGraph=nxGraph )
    Nodes = CNetObj(name="Nodes", parent=Graph)
    Edges = CNetObj(name="Edges", parent=Graph)
    return Graph, Nodes, Edges

def createEdge_NetObj( nodeID_1, nodeID_2, parent, props={} ):
    ext_fields = {
                    CGraphEdge_NO.s_NodeID_1 : nodeID_1,
                    CGraphEdge_NO.s_NodeID_2 : nodeID_2
                    }
    edge = parent.queryObj( EdgeDisplayName( nodeID_1, nodeID_2 ), CGraphEdge_NO, props=props, ext_fields=ext_fields )

def createNetObjectsForGraph( nxGraph ):
    Graph, Nodes, Edges = createGraph_NO_Branches( nxGraph )

    for nodeID in nxGraph.nodes():
        node = CGraphNode_NO( name=nodeID, parent=Nodes )

    for edgeID in nxGraph.edges():
        createEdge_NetObj( nodeID_1 = edgeID[0], nodeID_2 = edgeID[1], parent = Edges )

def loadGraphML_to_NetObj( sFName, bReload ):
    graphObj = CTreeNode.resolvePath( CNetObj_Manager.rootObj, "Graph")
    if graphObj:
        if bReload:
            graphObj.localDestroy()
            graphObj.sendDeleted_NetCmd()
        else:
            return False

    del graphObj

    nxGraph = loadGraphML_File( sFName )
    if not nxGraph:
        return False

    createNetObjectsForGraph( nxGraph )
    return True


