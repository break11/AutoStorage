
import networkx as nx
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.NetObj import CNetObj
from Lib.Common.TreeNode import CTreeNode, CTreeNodeCache
from Lib.Net.NetObj_Utils import destroy_If_Reload
from Lib.Common.GraphUtils import EdgeDisplayName, loadGraphML_File
from Lib.Common.StrConsts import SC
import Lib.GraphEntity.StorageGraphTypes as SGT

s_Graph = "Graph"
s_Nodes = "Nodes"
s_Edges = "Edges"

##remove##
# def graphNodeCache():
#     return CTreeNodeCache( baseNode = CNetObj_Manager.rootObj, path = s_Graph )

# graphNodeCache = CTreeNodeCache( baseNode = CNetObj_Manager.rootObj, path = s_Graph )
graphNodeCache = CTreeNodeCache( path = s_Graph )

class CGraphRoot_NO( CNetObj ):    
    def __init__( self, name="", parent=None, id=None, saveToRedis=True, props=None, ext_fields=None, nxGraph=None ):
        if nxGraph is not None:
            self.nxGraph = nxGraph
        else:
            if props is None: props = {} # приходится дублировать поведение предка здесь, т.к. в предок передается указатель на свойства графа - self.nxGraph.graph
            self.nxGraph = nx.DiGraph( **props )

        props = self.nxGraph.graph

        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis, props=props, ext_fields=ext_fields )        

        self.nodesNode = CTreeNodeCache( baseNode = self, path = s_Nodes )
        self.edgesNode = CTreeNodeCache( baseNode = self, path = s_Edges )

###################################################################################

common_NodeProps = { SGT.SGA.x, SGT.SGA.y, SGT.SGA.nodeType }
# spec_NodeProps - True в дикте означает обязательное присутствие свойства в объекте
spec_NodeProps = {
    SGT.ENodeTypes.PowerStation     : { SGT.SGA.chargePort : True,  SGT.SGA.chargeSide : True  },
    SGT.ENodeTypes.PickStation      : { SGT.SGA.linkLeft   : False, SGT.SGA.linkRight  : False },
    SGT.ENodeTypes.TransporterPoint : { SGT.SGA.linkPlace  : False }
}

class CGraphNode_NO( CNetObj ):
    def_props = {
                    SGT.SGA.x          : 0,
                    SGT.SGA.y          : 0,                          
                    SGT.SGA.nodeType   : SGT.ENodeTypes.DummyNode,
                    SGT.SGA.chargePort : "ttyS0",
                    SGT.SGA.chargeSide : SGT.ESide.Default,
                    SGT.SGA.linkLeft   : SGT.SNodePlace( SC.some_node, SGT.ESide.Undefined ),
                    SGT.SGA.linkRight  : SGT.SNodePlace( SC.some_node, SGT.ESide.Undefined ),
                    SGT.SGA.linkPlace  : SGT.SNodePlace( SC.some_node, SGT.ESide.Undefined )
                }

    def __init__( self, name="", parent=None, id=None, saveToRedis=True, props=None, ext_fields=None ):
        self.graphNode = CTreeNodeCache( baseNode = self, path = "../../" )

        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis, props=props, ext_fields=ext_fields )

    def beforeRegister( self ):
        # перед отправкой в редим подмена указателя на props
        if not self.__has_nxNode():
            self.nxGraph().add_node( self.name, **self.props )
            self.props = self.nxGraph().nodes[ self.name ]

    def ObjDeleted( self, netCmd ):
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

    def nxGraph(self)     : return self.graphNode().nxGraph if self.graphNode() else None
    def nxNode(self)      : return self.nxGraph().nodes()[ self.name ] if self.__has_nxNode() else {}
    def __has_nxNode(self): return self.nxGraph().has_node( self.name ) if self.nxGraph() else None

###################################################################################

common_EdgeProps = { SGT.SGA.edgeType, SGT.SGA.edgeSize }
spec_EdgeProps = {
    SGT.EEdgeTypes.Rail : { SGT.SGA.highRailSizeFrom : True, SGT.SGA.highRailSizeTo : True,
                            SGT.SGA.sensorSide : True, SGT.SGA.widthType : True, SGT.SGA.curvature : True }
}

class CGraphEdge_NO( CNetObj ):
    def_props = {
                    SGT.SGA.edgeType:         SGT.EEdgeTypes.Rail,
                    SGT.SGA.edgeSize:         500,               
                    SGT.SGA.highRailSizeFrom: 0,                 
                    SGT.SGA.highRailSizeTo:   0,                 
                    SGT.SGA.sensorSide:       SGT.ESensorSide.SBoth, 
                    SGT.SGA.widthType:        SGT.EWidthType.Narrow, 
                    SGT.SGA.curvature:        SGT.ECurvature.Straight
                }

    s_NodeID_1  = "NodeID_1"
    s_NodeID_2  = "NodeID_2"

    @classmethod
    def createEdge_NetObj( cls, nodeID_1, nodeID_2, parent, props=None ):
        ext_fields = {
                        cls.s_NodeID_1 : nodeID_1,
                        cls.s_NodeID_2 : nodeID_2
                        }
        edge = parent.queryObj( EdgeDisplayName( nodeID_1, nodeID_2 ), cls, props=props, ext_fields=ext_fields )

    def __init__( self, name="", parent=None, id=None, saveToRedis=True, props=None, ext_fields=None ):

        self.graphNode = CTreeNodeCache( baseNode = self, path = "../../" )

        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis, props=props, ext_fields=ext_fields )

    def beforeRegister( self ):
        # перед отправкой в редис подмена указателя на props
        if not self.__has_nxEdge():
            tKey = ( self.nxNodeID_1(), self.nxNodeID_2() )
            self.nxGraph().add_edge( self.nxNodeID_1(), self.nxNodeID_2(), **self.props )
            self.props = self.nxGraph().edges[ tKey ]

    def ObjDeleted( self, netCmd ):
        # при удалении NetObj объекта грани удаляем соответствующую грань из графа
        # такой грани уже может не быть в графе, если изначально удалялась нода, она сама внутри графа удалит инцидентную грань
        if self.__has_nxEdge():
            self.nxGraph().remove_edge( *self.__nxEdgeName() )

    def nxNodeID_1(self)  : return self.ext_fields[ self.s_NodeID_1 ]
    def nxNodeID_2(self)  : return self.ext_fields[ self.s_NodeID_2 ]
    def __has_nxEdge(self): return self.nxGraph().has_edge( self.nxNodeID_1(), self.nxNodeID_2() ) if self.nxGraph() else None
    def __nxEdgeName(self): return ( self.nxNodeID_1(), self.nxNodeID_2() )
    def nxGraph(self)     : return self.graphNode().nxGraph if self.graphNode() else None
    def nxEdge(self)      : return self.nxGraph().edges()[ self.__nxEdgeName() ] if self.__has_nxEdge() else {}

def createGraph_NO_Branches( nxGraph ):
    Graph  = CGraphRoot_NO( name=s_Graph, parent=CNetObj_Manager.rootObj, nxGraph=nxGraph )
    Nodes = CNetObj(name=s_Nodes, parent=Graph)
    Edges = CNetObj(name=s_Edges, parent=Graph)
    return Graph, Nodes, Edges

def createNetObjectsForGraph( nxGraph ):
    Graph, Nodes, Edges = createGraph_NO_Branches( nxGraph )

    for nodeID in nxGraph.nodes():
        node = CGraphNode_NO( name=nodeID, parent=Nodes, props = nxGraph.nodes()[ nodeID ] )

    for edgeID in nxGraph.edges():
        edge = CGraphEdge_NO.createEdge_NetObj( nodeID_1 = edgeID[0], nodeID_2 = edgeID[1], parent = Edges, props=nxGraph.edges()[ edgeID ] )

def loadGraphML_to_NetObj( sFName, bReload ):
    if not destroy_If_Reload( s_Graph, bReload ): return False

    nxGraph = loadGraphML_File( sFName )
    if not nxGraph:
        return False

    SGT.prepareGraphProps( nxGraph )
    createNetObjectsForGraph( nxGraph )
    return True


