
import networkx as nx
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.NetObj import CNetObj
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Common.TreeNode import CTreeNode
from Lib.Common.TreeNodeCache import CTreeNodeCache
from Lib.Net.NetObj_Utils import isSelfEvent
from Lib.Common.GraphUtils import EdgeDisplayName, loadGraphML_File, renameDuplicateNodes
from Lib.Common.StrConsts import SC
import Lib.Common.BaseTypes as BT
import Lib.Modbus.ModbusTypes as MT
import Lib.GraphEntity.StorageGraphTypes as SGT
import Lib.PowerStationEntity.PowerStationTypes as PST

s_Graph = "Graph"
s_Nodes = "Nodes"
s_Edges = "Edges"

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

        self.nodesNode = CTreeNodeCache( basePath = self.path(), path = s_Nodes )
        self.edgesNode = CTreeNodeCache( basePath = self.path(), path = s_Edges )

###################################################################################

common_NodeProps = { SGT.SGA.x, SGT.SGA.y, SGT.SGA.nodeType }
# spec_NodeProps - True в дикте означает обязательное присутствие свойства в объекте
spec_NodeProps = {
    SGT.ENodeTypes.PowerStation     : { SGT.SGA.chargeAddress : True,  SGT.SGA.chargeSide : True, SGT.SGA.chargeStage : True, SGT.SGA.powerState : True },
    SGT.ENodeTypes.PickStation      : { SGT.SGA.linkLeft   : False, SGT.SGA.linkRight  : False },
    SGT.ENodeTypes.TransporterPoint : { SGT.SGA.linkPlace  : False }
}

class CGraphNode_NO( CNetObj ):
    def_props = {
                    SGT.SGA.x          : 0,
                    SGT.SGA.y          : 0,                          
                    SGT.SGA.nodeType   : SGT.ENodeTypes.DummyNode,

                    SGT.SGA.chargeAddress : BT.CConnectionAddress.defTCP_IP(),
                    SGT.SGA.chargeSide    : SGT.ESide.Default,
                    SGT.SGA.chargeStage   : PST.EChargeStage.Default,
                    SGT.SGA.powerState    : PST.EChargeState.Default,

                    SGT.SGA.linkLeft   : SGT.SNodePlace( SC.some_node, SGT.ESide.Undefined ),
                    SGT.SGA.linkRight  : SGT.SNodePlace( SC.some_node, SGT.ESide.Undefined ),
                    SGT.SGA.linkPlace  : SGT.SNodePlace( SC.some_node, SGT.ESide.Undefined ),
                    SGT.SGA.x          : 0,
                    SGT.SGA.x          : 0,
                }

    def __init__( self, name="", parent=None, id=None, saveToRedis=True, props=None, ext_fields=None ):
        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis, props=props, ext_fields=ext_fields )
        CNetObj_Manager.addCallback( EV.ObjDeleted, self )

    def beforeRegister( self ):
        # перед отправкой в редис подмена указателя на props
        if not self.__has_nxNode():
            self.nxGraph().add_node( self.name, **self.props )
            self.props = self.nxGraph().nodes[ self.name ]

    def ObjDeleted( self, netCmd ):
        if not isSelfEvent( netCmd, self ): return

        incEdges = []
        if self.nxGraph():
            incEdges = list( self.nxGraph().out_edges( self.name ) ) +  list( self.nxGraph().in_edges( self.name ) )

        edges = graphNodeCache().edgesNode()
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

    def nxGraph(self)     : return graphNodeCache().nxGraph if graphNodeCache() else None
    def nxNode(self)      : return self.nxGraph().nodes()[ self.name ] if self.__has_nxNode() else {}
    def __has_nxNode(self): return self.nxGraph().has_node( self.name ) if self.nxGraph() else None

def nodeNetObj_byName( nodeID ):
    return graphNodeCache().nodesNode().childByName( nodeID )

###################################################################################

common_EdgeProps = { SGT.SGA.edgeType, SGT.SGA.edgeSize }
spec_EdgeProps = {
    SGT.EEdgeTypes.Rail : { SGT.SGA.highRailSizeFrom : True, SGT.SGA.highRailSizeTo : True,
                            SGT.SGA.sensorSide : True, SGT.SGA.widthType : True, SGT.SGA.curvature : True },
    SGT.EEdgeTypes.Transporter : { SGT.SGA.tsName : True, SGT.SGA.sensorAddress : True, SGT.SGA.sensorState : True}
}

class CGraphEdge_NO( CNetObj ):
    def_props = {
                    SGT.SGA.edgeType:         SGT.EEdgeTypes.Rail,
                    SGT.SGA.edgeSize:         500,               
                    SGT.SGA.highRailSizeFrom: 0,                 
                    SGT.SGA.highRailSizeTo:   0,                 
                    SGT.SGA.sensorSide:       SGT.ESensorSide.SBoth, 
                    SGT.SGA.widthType:        SGT.EWidthType.Narrow, 
                    SGT.SGA.curvature:        SGT.ECurvature.Straight,
                    SGT.SGA.tsName:           "",
                    SGT.SGA.sensorAddress:    MT.CRegisterAddress.defAddress(),
                    SGT.SGA.sensorState:      0
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
        super().__init__( name=name, parent=parent, id=id, saveToRedis=saveToRedis, props=props, ext_fields=ext_fields )
        CNetObj_Manager.addCallback( EV.ObjDeleted, self )

    def beforeRegister( self ):
        # перед отправкой в редис подмена указателя на props
        if not self.__has_nxEdge():
            tKey = ( self.nxNodeID_1(), self.nxNodeID_2() )
            self.nxGraph().add_edge( self.nxNodeID_1(), self.nxNodeID_2(), **self.props )
            self.props = self.nxGraph().edges[ tKey ]

    def ObjDeleted( self, netCmd ):
        if not isSelfEvent( netCmd, self ): return

        # при удалении NetObj объекта грани удаляем соответствующую грань из графа
        # такой грани уже может не быть в графе, если изначально удалялась нода, она сама внутри графа удалит инцидентную грань
        if self.__has_nxEdge():
            self.nxGraph().remove_edge( *self.__nxEdgeName() )

    def nxNodeID_1(self)  : return self.ext_fields[ self.s_NodeID_1 ]
    def nxNodeID_2(self)  : return self.ext_fields[ self.s_NodeID_2 ]
    def __has_nxEdge(self): return self.nxGraph().has_edge( self.nxNodeID_1(), self.nxNodeID_2() ) if self.nxGraph() else None
    def __nxEdgeName(self): return ( self.nxNodeID_1(), self.nxNodeID_2() )
    def nxGraph(self)     : return graphNodeCache().nxGraph if graphNodeCache() else None
    def nxEdge(self)      : return self.nxGraph().edges()[ self.__nxEdgeName() ] if self.__has_nxEdge() else {}

def createGraph_NO_Branches( nxGraph ):
    Graph = CNetObj_Manager.rootObj.queryObj( sName=s_Graph, ObjClass=CGraphRoot_NO, props=nxGraph.graph )
    Nodes = Graph.queryObj( sName=s_Nodes, ObjClass=CNetObj )
    Edges = Graph.queryObj( sName=s_Edges, ObjClass=CNetObj )
    # Nodes = CNetObj(name=s_Nodes, parent=Graph)
    # Edges = CNetObj(name=s_Edges, parent=Graph)
    return Graph, Nodes, Edges

def createNetObjectsForGraph( nxGraph ):
    Graph, Nodes, Edges = createGraph_NO_Branches( nxGraph )

    for nodeID in nxGraph.nodes():
        node = CGraphNode_NO( name=nodeID, parent=Nodes, props = nxGraph.nodes()[ nodeID ] )

    for edgeID in nxGraph.edges():
        edge = CGraphEdge_NO.createEdge_NetObj( nodeID_1 = edgeID[0], nodeID_2 = edgeID[1], parent = Edges, props=nxGraph.edges()[ edgeID ] )

def loadGraphML_to_NetObj( sFName ):
    graphNodeCache().destroy()
    # graphNodeCache().destroyChildren()

    nxGraph = loadGraphML_File( sFName )
    if not nxGraph:
        return False

    SGT.prepareGraphProps( nxGraph )
    createNetObjectsForGraph( nxGraph )
    return True

def loadDisjoint_Graph( sFName ):
    nxSubGraph = loadGraphML_File( sFName )
    if not nxSubGraph:
        return False

    SGT.prepareGraphProps( nxSubGraph )
    nxSubGraph = renameDuplicateNodes( graphNodeCache().nxGraph, nxSubGraph )

    createNetObjectsForGraph( nxSubGraph )
    return True