
import os
import networkx as nx
import weakref
import math
from enum import Enum, Flag, auto
from copy import deepcopy

from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtCore import (pyqtSlot, QObject, QLineF, QPointF, QEvent, Qt)
from PyQt5.QtWidgets import ( QGraphicsItem )

from .Node_SGItem import CNode_SGItem
from .Edge_SGItem import CEdge_SGItem
from .Agent_SGItem import CAgent_SGItem
from Lib.Common.GItem_EventFilter import CGItem_EventFilter
from Lib.Common.GuiUtils import gvFitToPage, Std_Model_Item
from Lib.Common.GraphUtils import EdgeDisplayName
from Lib.Common.Graph_NetObjects import loadGraphML_to_NetObj, createGraph_NO_Branches
from Lib.Common.TreeNode import CTreeNodeCache
from Lib.Common import StrConsts as SC
from Lib.Common import StorageGraphTypes as SGT
from Lib.Common.Graph_NetObjects import CGraphNode_NO, CGraphEdge_NO, createEdge_NetObj
from Lib.Net.NetObj import CNetObj
from Lib.Net.NetObj_Manager import CNetObj_Manager

class EGManagerMode (Flag):
    View      = auto()
    EditScene = auto()
    EditProps = auto()

class EGManagerEditMode (Flag):
    Default = auto()
    AddNode = auto()

class CStorageGraph_GScene_Manager():
    default_Edge_Props = {
                            SGT.s_edgeType:         'Normal',                    # type: ignore
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
                            SGT.s_containsAgent: -1,                       # type: ignore
                            SGT.s_floor_num: 0                             # type: ignore
                        }

    @property
    def nxGraph(self): return self.graphRootNode().nxGraph

    def __init__(self, gScene, gView):
        self.bEdgeReversing = False
        self.bGraphLoading = False
        self.agentGItems    = {}
        self.nodeGItems     = {}
        self.edgeGItems     = {}
        self.gScene_evI     = None

        self.bDrawBBox         = False
        self.bDrawInfoRails    = False
        self.bDrawMainRail     = False
        self.bDrawSpecialLines = False

        self.Mode           = EGManagerMode.View | EGManagerMode.EditScene | EGManagerMode.EditProps
        self.EditMode       = EGManagerEditMode.Default
        self.bHasChanges    = False

        self.gScene = gScene
        self.gView  = gView

        # self.gScene.setMinimumRenderSize( 3 )
        # self.gView.setViewport( QGLWidget( QGLFormat(QGL.SampleBuffers) ) )
        # self.gView.setViewport( QOpenGLWidget( ) )
        # self.gScene.setBspTreeDepth( 1 )

        self.__maxNodeID    = 0
        self.graphRootNode = CTreeNodeCache( baseNode = CNetObj_Manager.rootObj, path = "Graph" )

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
        self.gScene_evI = CGItem_EventFilter()
        self.gScene.addItem( self.gScene_evI )

    def clear(self):
        self.agentGItems = {}
        self.nodeGItems = {}
        self.edgeGItems = {}
        self.gScene.clear()
        self.gScene.update()
        
    def new(self):
        # self.clear()
        # self.init()
        # не вызываем здесь, т.к. вызовется при реакции на создание корневого элемента графа

        if self.graphRootNode():
            self.graphRootNode().localDestroy()

        createGraph_NO_Branches( nxGraph = nx.DiGraph() )
        
        self.bHasChanges = True

    def genTestGraph(self):
        #test adding nodes
        side_count = 200
        step = 2200
        last_node = None
        for x in range(0, side_count * step, step):
            for y in range(0, side_count * 400, 400):
                cur_node = self.addNode( self.genStrNodeID(), x = x, y = y, nodeType = "StorageSingle" )
                if last_node:
                    tKey = (cur_node.nodeID, last_node.nodeID)
                    self.nxGraph.add_edge( cur_node.nodeID, last_node.nodeID, **self.default_Edge_Props )
                    self.nxGraph.add_edge( last_node.nodeID, cur_node.nodeID, **self.default_Edge_Props )
                    self.addEdge( tKey )
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
        
        gvFitToPage( self.gView )
        self.bHasChanges = False  # сбрасываем признак изменения сцены после загрузки

        self.bGraphLoading = False

        print( f"GraphicsItems in scene = {len(self.gScene.items())}" )

        return True

    def save( self, sFName ):
        nx.write_graphml(self.nxGraph, sFName)

    def setDrawInfoRails( self, bVal ):
        self.bDrawInfoRails = bVal
        for k, v in self.edgeGItems.items():
            v.updateDecorateOnScene()

    def setDrawMainRail( self, bVal ):
        self.bDrawMainRail = bVal
        for k, v in self.edgeGItems.items():
            v.updateDecorateOnScene()

    def setDrawBBox( self, bVal ):
        self.bDrawBBox = bVal
        self.gScene.update()

    def setDrawSpecialLines(self, bVal):
        self.bDrawSpecialLines = bVal
        self.gScene.update()

    #рассчет средней линии для нод
    def calcNodeMiddleLine(self, nodeGItem):        
        if nodeGItem.nodeType != SGT.ENodeTypes.StorageSingle:
            return
        incEdges = list( self.nxGraph.out_edges( nodeGItem.nodeID ) ) +  list( self.nxGraph.in_edges( nodeGItem.nodeID ) )
        dictEdges = {}
        for key in incEdges:
            fsEdgeKey = frozenset( key )
            edgeGItem = self.edgeGItems.get( fsEdgeKey )
            if edgeGItem is not None:
                dictEdges[ fsEdgeKey ] = edgeGItem # оставляем только некратные грани
        
        listEdges = dictEdges.values()
        AllPairEdges = [ (e1, e2) for e1 in listEdges for e2 in listEdges ]
        dictDeltaAngles={} #составляем дикт, где ключ - острый угол между гранями, значение - кортеж из двух граней

        for e1, e2 in AllPairEdges:
            delta_angle = int( abs(e1.rotateAngle() - e2.rotateAngle()) )
            delta_angle = delta_angle if delta_angle <= 180 else (360-delta_angle)
            dictDeltaAngles[ delta_angle ] = (e1, e2)
        
        if len(dictDeltaAngles) == 0:
            nodeGItem.setMiddleLineAngle( 0 )
            return

        max_angle = max(dictDeltaAngles.keys())

        #вычисляем средний угол между гранями, если грань исходит не из nodeGItem, поворачиваем на 180
        if len (dictDeltaAngles) == 1:
            e1 = dictDeltaAngles[ max_angle ][0]
            r1 = e1.rotateAngle() if (e1.nodeID_1 == nodeGItem.nodeID) else (e1.rotateAngle() + 180) % 360
            r2 = r1 + 180
        else:
            e1 = dictDeltaAngles[ max_angle ][0]
            e2 = dictDeltaAngles[ max_angle ][1]
            r1 = e1.rotateAngle() if (e1.nodeID_1 == nodeGItem.nodeID) else (e1.rotateAngle() + 180) % 360
            r2 = e2.rotateAngle() if (e2.nodeID_1 == nodeGItem.nodeID) else (e2.rotateAngle() + 180) % 360

        nodeGItem.setMiddleLineAngle( min(r1, r2) + abs(r1-r2)/2 )

    # перестроение связанных с нодой граней
    def updateNodeIncEdges(self, nodeGItem):
        incEdges = list( self.nxGraph.out_edges( nodeGItem.nodeID ) ) +  list( self.nxGraph.in_edges( nodeGItem.nodeID ) )

        dictEdges = {}
        for key in incEdges:
            dictEdges[frozenset( key )] = self.edgeGItems[ frozenset(key) ]

        for edgeGItem in dictEdges.values():
            edgeGItem.buildEdge()
            edgeGItem.updatePos_From_NX()
        
        self.bHasChanges = True

        NeighborsIDs = list ( self.nxGraph.successors(nodeGItem.nodeID) ) + list ( self.nxGraph.predecessors(nodeGItem.nodeID) )
        nodeGItemsNeighbors = [ self.nodeGItems[nodeID] for nodeID in NeighborsIDs ]
        nodeGItemsNeighbors.append (nodeGItem)

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

        agentGItem = CAgent_SGItem ( agentNetObj = agentNetObj )
        self.gScene.addItem( agentGItem )
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

        nodeGItem = CNode_SGItem ( nodeNetObj = nodeNetObj )
        self.gScene.addItem( nodeGItem )
        self.nodeGItems[ nodeID ] = nodeGItem

        nodeGItem.init()
        nodeGItem.installSceneEventFilter( self.gScene_evI )
        nodeGItem.setFlag( QGraphicsItem.ItemIsMovable, bool (self.Mode & EGManagerMode.EditScene) )
        nodeGItem.SGM = self

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

        edgeGItem = CEdge_SGItem( fsEdgeKey=fsEdgeKey, graphRootNode=self.graphRootNode )
        self.gScene.addItem( edgeGItem )

        edgeGItem.updatePos_From_NX()
        edgeGItem.installSceneEventFilter( self.gScene_evI )
        self.edgeGItems[ fsEdgeKey ] = edgeGItem
        edgeGItem.SGM = self

        edgeGItem.updateDecorateOnScene()

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
                createEdge_NetObj( nodeID_1, nodeID_2, parent = self.graphRootNode().edgesNode(), props=self.default_Edge_Props )

            if reverse: #создание граней в обратном направлении
                createEdge_NetObj( nodeID_2, nodeID_1, parent = self.graphRootNode().edgesNode(), props=self.default_Edge_Props )

        fsEdgeKey = frozenset( ( nodeID_1, nodeID_2 ) )
        edgeGItem = self.edgeGItems.get( fsEdgeKey )
        if edgeGItem is None: return

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
            # в процессе операции разворачивания граней - не нужно удалять график итем грани
            if not self.bEdgeReversing:
                self.deleteEdge( fsEdgeKey )
        else:
            self.edgeGItems[ fsEdgeKey ].update()
            self.ViewerWindow.StorageMap_Scene_SelectionChanged()

    def deleteEdge(self, fsEdgeKey : frozenset ):
        edgeGItem = self.edgeGItems.get( fsEdgeKey )
        if edgeGItem is None: return

        edgeGItem.done()
        self.gScene.removeItem( edgeGItem )
        del self.edgeGItems[ fsEdgeKey ]

        # перерасчет средней линии для всех нод "связанных" с удаленными гранями
        for nodeID in fsEdgeKey:
            self.calcNodeMiddleLine( self.nodeGItems[ nodeID ] )

        self.bHasChanges = True

    def reverseEdge(self, fsEdgeKey):
        self.bEdgeReversing = True

        edgeGItem = self.edgeGItems[ fsEdgeKey ]

        b12 = edgeGItem.edge1_2() is not None
        b21 = edgeGItem.edge2_1() is not None

        if b12:
            attr12 = edgeGItem.edge1_2().propsDict()
            edgeGItem.edge1_2().sendDeleted_NetCmd()

        if b21:
            attr21 = edgeGItem.edge2_1().propsDict()
            edgeGItem.edge2_1().sendDeleted_NetCmd()

        if b12:
            createEdge_NetObj( edgeGItem.nodeID_2, edgeGItem.nodeID_1, parent = self.graphRootNode().edgesNode(), props=attr12 )
        
        if b21:
            createEdge_NetObj( edgeGItem.nodeID_1, edgeGItem.nodeID_2, parent = self.graphRootNode().edgesNode(), props=attr21 )

        edgeGItem.update()
        edgeGItem.decorateSGItem.update()
        edgeGItem.fillPropsTable( self.ViewerWindow.objProps )

        self.bEdgeReversing = False
        self.bHasChanges = True

    def deleteMultiEdge(self, fsEdgeKey): #удаление кратной грани
        edgeGItem = self.edgeGItems[ fsEdgeKey ]
        # if edgeGItem.hasNxEdge_2_1():
        #     self.nxGraph.remove_edge( edgeGItem.nodeID_2, edgeGItem.nodeID_1 )
        #     self.bHasChanges = True
        #     edgeGItem.update()
        #     edgeGItem.decorateSGItem.update()


class CGItem_CreateDelete_EF(QObject): # Creation/Destruction GItems

    def __init__(self, SGM):
        super().__init__(SGM.gView)
        self.__SGM = SGM
        self.__gView  = SGM.gView
        self.__gScene = SGM.gScene

        self.__gView.installEventFilter(self)
        self.__gView.viewport().installEventFilter(self)

    def eventFilter(self, object, event):
        if not (self.__SGM.Mode & EGManagerMode.EditScene):
            return False

        #добавление нод
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton and (self.__SGM.EditMode & EGManagerEditMode.AddNode) :
                attr = deepcopy (self.__SGM.default_Node_Props)
                attr[ SGT.s_x ] = SGT.adjustAttrType( SGT.s_x, self.__gView.mapToScene(event.pos()).x() )
                attr[ SGT.s_y ] = SGT.adjustAttrType( SGT.s_y, self.__gView.mapToScene(event.pos()).y() )

                CGraphNode_NO( name=self.__SGM.genStrNodeID(), parent=self.__SGM.graphRootNode().nodesNode(), props=attr )

                ##TODO: разобраться и починить ув-е размера сцены при добавление элементов на ее краю
                # self.__gScene.setSceneRect( self.__gScene.itemsBoundingRect() )
                # self.__gView.setSceneRect( self.__gView.scene().sceneRect() )

                event.accept()
                return True

        #удаление итемов
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Delete:
            for item in self.__gScene.selectedItems():
                item.destroy_NetObj()
            event.accept()
            return True
        
        return False