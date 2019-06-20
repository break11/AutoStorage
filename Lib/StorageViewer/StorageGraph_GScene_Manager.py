
import os
import networkx as nx
import weakref
import math
from enum import Enum, Flag, auto
from copy import deepcopy

from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import pyqtSlot, QObject, QLineF, QPointF, QEvent, Qt
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsLineItem, QGraphicsScene

from .Node_SGItem import CNode_SGItem
from .Edge_SGItem import CEdge_SGItem
from .Agent_SGItem import CAgent_SGItem
from Lib.Common.GItem_EventFilter import CGItem_EventFilter
from Lib.Common.GuiUtils import gvFitToPage
from Lib.Common.Utils import time_func
from Lib.Common.Graph_NetObjects import loadGraphML_to_NetObj, createGraph_NO_Branches, graphNodeCache
from Lib.Common.TreeNode import CTreeNodeCache
from Lib.Common import StrConsts as SC
from Lib.Common import StorageGraphTypes as SGT
from Lib.Common.Graph_NetObjects import CGraphRoot_NO, CGraphNode_NO, CGraphEdge_NO
from Lib.Common.Agent_NetObject import CAgent_NO, s_position, s_edge, s_angle, s_route, def_props as agent_def_props,agentsNodeCache
from Lib.Common.Dummy_GItem import CDummy_GItem
from Lib.Common.GraphUtils import getEdgeCoords, getNodeCoords, vecsFromNodes, vecsPair_withMaxAngle
from Lib.Net.NetObj import CNetObj
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Common.Vectors import Vector2


class EGManagerMode (Flag):
    View      = auto()
    EditScene = auto()
    EditProps = auto()

class EGManagerEditMode (Flag):
    Default = auto()
    AddNode = auto()

class CStorageGraph_GScene_Manager( QObject ):
    default_Edge_Props = {
                            SGT.s_edgeSize:         500,                         # type: ignore
                            SGT.s_highRailSizeFrom: 0,                           # type: ignore
                            SGT.s_highRailSizeTo:   0,                           # type: ignore
                            SGT.s_sensorSide:       SGT.ESensorSide.SBoth.name,  # type: ignore
                            SGT.s_widthType:        SGT.EWidthType.Narrow.name,  # type: ignore
                            SGT.s_curvature:        SGT.ECurvature.Straight.name # type: ignore
                        }

    default_Node_Props = {  
                            SGT.s_x: 0,                                    # type: ignore
                            SGT.s_y: 0,                                    # type: ignore
                            SGT.s_nodeType: SGT.ENodeTypes.DummyNode.name, # type: ignore
                        }

    @property
    def nxGraph(self): return self.graphRootNode().nxGraph

    def __init__(self, gScene, gView):
        super().__init__()

        self.bEdgeReversing = False
        self.bGraphLoading = False
        self.agentGItems    = {}
        self.nodeGItems     = {}
        self.edgeGItems     = {}

        self.bDrawBBox         = False
        self.bDrawInfoRails    = False
        self.bDrawMainRail     = False
        self.bDrawSpecialLines = False

        self.Mode           = EGManagerMode.View | EGManagerMode.EditScene | EGManagerMode.EditProps
        self.EditMode       = EGManagerEditMode.Default
        self.bHasChanges    = False

        self.gScene = gScene
        self.gView  = gView

        gView.installEventFilter(self)
        gView.viewport().installEventFilter(self)

        # self.gScene.setMinimumRenderSize( 3 )
        # self.gView.setViewport( QGLWidget( QGLFormat(QGL.SampleBuffers) ) )
        # self.gView.setViewport( QOpenGLWidget( ) )
        # self.gScene.setBspTreeDepth( 1 )

        self.__maxNodeID    = 0
        self.graphRootNode = graphNodeCache()
        self.agentsNode    = agentsNodeCache()

        CNetObj_Manager.addCallback( EV.ObjCreated,       self.ObjCreated )
        CNetObj_Manager.addCallback( EV.ObjPrepareDelete, self.ObjPrepareDelete )
        CNetObj_Manager.addCallback( EV.ObjPropUpdated,   self.ObjPropUpdated )

        self.gScene_evI = CGItem_EventFilter()
        self.gScene.addItem( self.gScene_evI )

        self.Agents_ParentGItem = CDummy_GItem()
        self.Agents_ParentGItem.setZValue( 40 )
        self.gScene.addItem( self.Agents_ParentGItem )

        self.GraphRoot_ParentGItem     = None
        self.EdgeDecorates_ParentGItem = None

    def setModeFlags(self, flags):
        self.Mode = flags
        if not (self.Mode & EGManagerMode.EditScene):
            self.EditMode = EGManagerEditMode.Default
        
        self.updateGItemsMoveableFlags()

    def updateGItemsMoveableFlags(self):
        if self.Mode & EGManagerMode.EditScene:
            for nodeID, nodeGItem in self.nodeGItems.items():
                nodeGItem.setFlags( nodeGItem.flags() | QGraphicsItem.ItemIsMovable )
        else:
            for nodeID, nodeGItem in self.nodeGItems.items():
                nodeGItem.setFlags( nodeGItem.flags() & ~QGraphicsItem.ItemIsMovable )

    def init(self):
        self.GraphRoot_ParentGItem     = CDummy_GItem()
        self.EdgeDecorates_ParentGItem = CDummy_GItem( parent=None )

        if self.gScene_evI.scene() is None:
            self.gScene.addItem( self.gScene_evI )

        self.gScene.addItem( self.GraphRoot_ParentGItem )
        self.updateDecorateOnScene()

        if self.Agents_ParentGItem.scene() is None:
            self.gScene.addItem( self.Agents_ParentGItem )

    @time_func( sMsg="Scene clear time =" )
    def clear(self):
        self.nodeGItems = {}
        self.edgeGItems = {}

        self.gScene.removeItem( self.gScene_evI )
        self.gScene.removeItem( self.Agents_ParentGItem )
        self.gScene.clear()

        self.GraphRoot_ParentGItem     = None
        self.EdgeDecorates_ParentGItem = None

        self.gScene.update()
        
    def new(self):
        # self.clear()
        # self.init()
        # не вызываем здесь, т.к. вызовется при реакции на создание корневого элемента графа

        if self.graphRootNode():
            self.graphRootNode().destroy()

        createGraph_NO_Branches( nxGraph = nx.DiGraph() )
        
        self.bHasChanges = True

    def genTestGraph(self, nodes_side_count = 200, step = 2200):
        #test adding nodes
        last_node = None
        for x in range(0, nodes_side_count * step, step):
            for y in range(0, nodes_side_count * 400, 400):
                props = {"x": x, "y": y, "nodeType":"StorageSingle"}
                cur_node = CGraphNode_NO( name = self.genStrNodeID(), parent = self.graphRootNode().nodesNode(),
                        saveToRedis = True, props = props, ext_fields = {} )
                if last_node:
                    CGraphEdge_NO.createEdge_NetObj( nodeID_1 = cur_node.name, nodeID_2 = last_node.name, parent = self.graphRootNode().edgesNode() )

                last_node = cur_node

    def load(self, sFName):
        # self.clear()
        # self.init()
        # не вызываем здесь, т.к. вызовется при реакции на создание корневого элемента графа

        self.bGraphLoading = True # For block "calcNodeMiddleLine()" on Edge creating while loading ( 5 sec overhead on "40 000 with edges" )

        if not loadGraphML_to_NetObj( sFName, bReload=True ):
            self.bGraphLoading = False
            return False

        self.updateMaxNodeID()

        # после создания граней перерасчитываем линии расположения мест хранения
        for nodeID, nodeGItem in self.nodeGItems.items():
            self.calcNodeMiddleLine( nodeGItem )
        
        ##remove## gvFitToPage( self.gView ) - не нужно т.к. выполоняется как реакция на GraphNet_Obj
        self.bHasChanges = False  # сбрасываем признак изменения сцены после загрузки

        self.bGraphLoading = False

        print( f"GraphicsItems in scene = {len(self.gScene.items())}" )
        return True

    def save( self, sFName ):
        try:
            nx.write_graphml(self.nxGraph, sFName)
            return True
        except Exception as e:
            print( f"{SC.sError} { e }" )
            return False

    def setDrawInfoRails( self, bVal ):
        self.bDrawInfoRails = bVal
        self.updateDecorateOnScene()

    def setDrawMainRail( self, bVal ):
        self.bDrawMainRail = bVal
        self.updateDecorateOnScene()

    def updateDecorateOnScene(self):
        if ( self.GraphRoot_ParentGItem is None ) or ( self.EdgeDecorates_ParentGItem is None ):
            return

        bVal = self.bDrawMainRail or self.bDrawInfoRails
        if bVal:
            self.EdgeDecorates_ParentGItem.setParentItem( self.GraphRoot_ParentGItem )
        elif self.EdgeDecorates_ParentGItem.scene():
            self.gScene.removeItem( self.EdgeDecorates_ParentGItem )

        self.gScene.update()

    def setDrawBBox( self, bVal ):
        self.bDrawBBox = bVal
        self.gScene.update()

    def setDrawSpecialLines(self, bVal):
        self.bDrawSpecialLines = bVal
        self.gScene.update()

    def calcNodeMiddleLine(self, nodeGItem):        
        if nodeGItem.nodeType != SGT.ENodeTypes.StorageSingle:
            return
        
        # берем смежные вершины и оставляем только те из них, для которых есть грань в edgeGItems,
        # тк в случае удаления грани или вершины они сначала удаляются из edgeGItems(nodeGItems),
        # а из графа удаляются позже и могут ещё присутствовать в графе
        NeighborsIDs = set( self.nxGraph.successors(nodeGItem.nodeID) ).union( set(self.nxGraph.predecessors(nodeGItem.nodeID)) )
        NeighborsIDs = [ ID for ID in NeighborsIDs if self.edgeGItems.get( frozenset((nodeGItem.nodeID, ID)) ) ]
        
        nodeVecs = vecsFromNodes( nxGraph = self.nxGraph, nodeID = nodeGItem.nodeID, NeighborsIDs = NeighborsIDs )
        vecs_count = len(nodeVecs)

        r_vec = Vector2(1, 0)
        
        if vecs_count > 1:
            vec1, vec2 = vecsPair_withMaxAngle( nodeVecs )
            r_vec = vec1 + vec2

            #если вектора противоположнонаправлены, r_vec будет нулевым вектором,
            # тогда результирующий вектор берём как перпендикуляр vec1 или vec2
            r_vec = r_vec if r_vec else vec1.rotate( math.pi/2 )

        elif vecs_count == 1:
            r_vec = nodeVecs[0].rotate( math.pi/2 )
        
        res_angle = math.degrees( r_vec.selfAngle() )
        nodeGItem.setMiddleLineAngle( res_angle )

    # перестроение связанных с нодой граней
    def updateNodeIncEdges(self, nodeGItem):
        incEdges = list( self.nxGraph.out_edges( nodeGItem.nodeID ) ) +  list( self.nxGraph.in_edges( nodeGItem.nodeID ) )

        dictEdges = {}
        for key in incEdges:
            dictEdges[frozenset( key )] = self.edgeGItems[ frozenset(key) ]

        for edgeGItem in dictEdges.values():
            edgeGItem.buildEdge()
            edgeGItem.updatePos()
        
        self.bHasChanges = True

        NeighborsIDs = list ( self.nxGraph.successors(nodeGItem.nodeID) ) + list ( self.nxGraph.predecessors(nodeGItem.nodeID) )
        nodeGItemsNeighbors = set ( [ self.nodeGItems[nodeID] for nodeID in NeighborsIDs ] )
        nodeGItemsNeighbors.add (nodeGItem)

        for nodeGItem in nodeGItemsNeighbors:
            self.calcNodeMiddleLine(nodeGItem)

    def updateMaxNodeID(self):
        maxNodeID = 0
        for nodeID in self.nodeGItems.keys():
            try:
                maxNodeID = int (nodeID) if int (nodeID) > maxNodeID else maxNodeID
            except ValueError:
                pass
        self.__maxNodeID = maxNodeID
    
    def genStrNodeID(self):
        self.__maxNodeID += 1
        return str(self.__maxNodeID)
        
    def addAgent( self, agentNetObj ):
        if self.agentGItems.get ( agentNetObj.name ): return

        agentGItem = CAgent_SGItem ( SGM=self, agentNetObj = agentNetObj, parent=self.Agents_ParentGItem )
        
        self.agentGItems[ agentNetObj.name ] = agentGItem

        agentGItem.init()
        agentGItem.installSceneEventFilter( self.gScene_evI )
        agentGItem.SGM = self

        return agentGItem

    def deleteAgent(self, agentNetObj):
        self.gScene.removeItem ( self.agentGItems[ agentNetObj.name ] )
        del self.agentGItems[ agentNetObj.name ]

    def addNode( self, nodeNetObj ):
        nodeID = nodeNetObj.name
        if self.nodeGItems.get ( nodeID ): return

        nodeGItem = CNode_SGItem ( self, nodeNetObj = nodeNetObj, parent=self.GraphRoot_ParentGItem )
        self.nodeGItems[ nodeID ] = nodeGItem

        nodeGItem.init()
        nodeGItem.installSceneEventFilter( self.gScene_evI )
        nodeGItem.setFlag( QGraphicsItem.ItemIsMovable, bool (self.Mode & EGManagerMode.EditScene) )

        self.bHasChanges = True
        return nodeGItem

    def deleteNode(self, nodeNetObj):
        nodeID = nodeNetObj.name
        if self.nodeGItems.get ( nodeID ) is None: return

        self.gScene.removeItem ( self.nodeGItems[ nodeID ] )
        del self.nodeGItems[ nodeID ]
        self.bHasChanges = True

    def addEdge( self, edgeNetObj ):
        fsEdgeKey = frozenset( ( edgeNetObj.nxNodeID_1(), edgeNetObj.nxNodeID_2() ) )
        if self.edgeGItems.get( fsEdgeKey ) : return False

        edgeGItem = CEdge_SGItem( self, fsEdgeKey=fsEdgeKey, graphRootNode=self.graphRootNode, parent=self.GraphRoot_ParentGItem )

        edgeGItem.updatePos()
        edgeGItem.installSceneEventFilter( self.gScene_evI )
        self.edgeGItems[ fsEdgeKey ] = edgeGItem

        self.bHasChanges = True

        if not self.bGraphLoading:
            self.calcNodeMiddleLine( self.nodeGItems[ edgeNetObj.nxNodeID_1() ] )
            self.calcNodeMiddleLine( self.nodeGItems[ edgeNetObj.nxNodeID_2() ] )

        return True
    
    def addEdges_NetObj_ForSelection(self, direct = True, reverse = True):
        nodeGItems = [ n for n in self.gScene.orderedSelection if isinstance(n, CNode_SGItem) ] # выбираем из selectedItems ноды
        nodePairCount = len(nodeGItems) - 1
        
        for i in range(nodePairCount):
            nodeID_1 = nodeGItems[i].nodeID
            nodeID_2 = nodeGItems[i+1].nodeID
            if direct: #создание граней в прямом направлении
                CGraphEdge_NO.createEdge_NetObj( nodeID_1, nodeID_2, parent = self.graphRootNode().edgesNode(), props=self.default_Edge_Props )

            if reverse: #создание граней в обратном направлении
                CGraphEdge_NO.createEdge_NetObj( nodeID_2, nodeID_1, parent = self.graphRootNode().edgesNode(), props=self.default_Edge_Props )

            if direct == False and reverse == False: continue

            fsEdgeKey = frozenset( ( nodeID_1, nodeID_2 ) )
            edgeGItem = self.edgeGItems.get( fsEdgeKey )

            edgeGItem.update()
            edgeGItem.decorateSGItem.update()

    
    # удаление NetObj объектов определяющих грань
    def deleteEdge_NetObj(self, edgeNetObj):
        # если удаляется последняя из кратных граней, то удаляем graphicsItem который их рисовал, иначе вызываем его перерисовку
        tKey = ( edgeNetObj.nxNodeID_1(), edgeNetObj.nxNodeID_2() )
        fsEdgeKey = frozenset( tKey )
        edgeGItem = self.edgeGItems.get( fsEdgeKey )
        if edgeGItem is None: return

        if edgeGItem.edgesNetObj_by_TKey[ tuple(reversed( tKey )) ]() is None:
            # в процессе операции разворачивания граней - не нужно удалять "графикc итем" грани
            if not self.bEdgeReversing:
                self.deleteEdge( fsEdgeKey )
        else:
            edgeGItem.update()

    def deleteEdge(self, fsEdgeKey : frozenset ):
        edgeGItem = self.edgeGItems.get( fsEdgeKey )
        if edgeGItem is None: return

        edgeGItem.done()
        self.gScene.removeItem( edgeGItem )
        del self.edgeGItems[ fsEdgeKey ]

        # перерасчет средней линии для всех нод "связанных" с удаленными гранями
        for nodeID in fsEdgeKey:
            nodeGItem = self.nodeGItems.get( nodeID )
            if nodeGItem is not None:
                self.calcNodeMiddleLine( nodeGItem )

        self.bHasChanges = True

    def reverseEdge(self, fsEdgeKey):
        self.bEdgeReversing = True

        edgeGItem = self.edgeGItems[ fsEdgeKey ]

        b12 = edgeGItem.edge1_2() is not None
        b21 = edgeGItem.edge2_1() is not None

        if b12:
            attr12 = edgeGItem.edge1_2().propsDict()
            edgeGItem.edge1_2().destroy()

        if b21:
            attr21 = edgeGItem.edge2_1().propsDict()
            edgeGItem.edge2_1().destroy()

        if b12:
            CGraphEdge_NO.createEdge_NetObj( edgeGItem.nodeID_2, edgeGItem.nodeID_1, parent = self.graphRootNode().edgesNode(), props=attr12 )
        
        if b21:
            CGraphEdge_NO.createEdge_NetObj( edgeGItem.nodeID_1, edgeGItem.nodeID_2, parent = self.graphRootNode().edgesNode(), props=attr21 )

        edgeGItem.update()
        edgeGItem.decorateSGItem.update()

        self.bEdgeReversing = False
        self.bHasChanges = True

    def deleteMultiEdge(self, fsEdgeKey): #удаление кратной грани
        edgeGItem = self.edgeGItems[ fsEdgeKey ]

        if (edgeGItem.edge1_2() is None) or (edgeGItem.edge2_1() is None):
            return

        # пока удаляем вторую подгрань грани, возможно потребуется более продвинутые способы
        edgeGItem.edge2_1().destroy()
        self.bHasChanges = True
        edgeGItem.update()
        edgeGItem.decorateSGItem.update()

    #############################################################

    def eventFilter(self, object, event):
        if not (self.Mode & EGManagerMode.EditScene):
            return False

        #добавление нод
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton and (self.EditMode & EGManagerEditMode.AddNode) :
                attr = deepcopy (self.default_Node_Props)
                attr[ SGT.s_x ] = round (self.gView.mapToScene(event.pos()).x())
                attr[ SGT.s_y ] = round (self.gView.mapToScene(event.pos()).y())

                CGraphNode_NO( name=self.genStrNodeID(), parent=self.graphRootNode().nodesNode(), props=attr )

                ##TODO: разобраться и починить ув-е размера сцены при добавление элементов на ее краю
                # self.gScene.setSceneRect( self.gScene.itemsBoundingRect() )
                # self.gView.setSceneRect( self.gView.scene().sceneRect() )

                event.accept()
                return True

        #удаление итемов
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Delete:
            for item in self.gScene.selectedItems():
                item.destroy_NetObj()
            event.accept()
            return True
        
        return False

    #############################################################

    @time_func( sMsg="Create scene items time", threshold=10 )
    def ObjCreated(self, netCmd=None):
        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID )

        if isinstance( netObj, CGraphRoot_NO ):
            self.init()
        elif isinstance( netObj, CGraphNode_NO ):
            self.addNode( nodeNetObj = netObj )
        elif isinstance( netObj, CGraphEdge_NO ):
            self.addEdge( edgeNetObj = netObj )
        elif isinstance( netObj, CAgent_NO ):
            self.addAgent( agentNetObj = netObj )
        elif isinstance( netObj, CNetObj ) and netObj.name == "Graph_End_Obj":
            gvFitToPage( self.gView )
            for agentGItem in self.agentGItems.values():
                agentGItem.updatePos()

    def ObjPrepareDelete(self, netCmd):
        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID )

        if isinstance( netObj, CGraphRoot_NO ):
            self.clear()
        elif isinstance( netObj, CGraphNode_NO ):
            self.deleteNode( nodeNetObj = netObj )
        elif isinstance( netObj, CGraphEdge_NO ):
            self.deleteEdge_NetObj( edgeNetObj = netObj )
        elif isinstance( netObj, CAgent_NO ):
            self.deleteAgent( agentNetObj = netObj )
    
    def ObjPropUpdated(self, netCmd):
        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID )
        # propName  = netCmd.sPropName
        # propValue = netObj[ netCmd.sPropName ]
        gItem = None

        if isinstance( netObj, CGraphNode_NO ):
            gItem = self.nodeGItems[ netObj.name ]
            gItem.init()
            self.updateNodeIncEdges( gItem )

        elif isinstance( netObj, CGraphEdge_NO ):
            tKey = ( netObj.nxNodeID_1(), netObj.nxNodeID_2() )
            fsEdgeKey = frozenset( tKey )

            gItem = self.edgeGItems[ fsEdgeKey ]
            gItem.decorateSGItem.updatedDecorate()

        elif isinstance( netObj, CAgent_NO ):
            if netCmd.sPropName == s_route:
                return

            gItem = self.agentGItems[ netObj.name ]
            
            if netCmd.sPropName == s_angle:
                gItem.updateRotation()
            elif netCmd.sPropName in [ s_position, s_edge ]:
                gItem.updatePos()