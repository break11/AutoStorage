
import os
import networkx as nx
import weakref
import math
from enum import Flag, auto, Enum
from copy import deepcopy
from collections import namedtuple

from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import pyqtSlot, QObject, QLineF, QPointF, QEvent, Qt, pyqtSignal, QTimer
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsLineItem, QGraphicsScene

from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.NetObj import CNetObj
from Lib.GraphEntity.Node_SGItem import CNode_SGItem
from Lib.GraphEntity.Edge_SGItem import CEdge_SGItem
from Lib.GraphEntity.EdgeDecorate_SGItem import CEdgeDecorate_SGItem
from Lib.Common.GuiUtils import gvFitToPage
from Lib.Common.Utils import time_func
from Lib.GraphEntity.Graph_NetObjects import loadGraphML_to_NetObj, createGraph_NO_Branches, graphNodeCache
from Lib.Common.TreeNodeCache import CTreeNodeCache
from Lib.Common.StrConsts import SC
from Lib.GraphEntity import StorageGraphTypes as SGT
from Lib.GraphEntity.Graph_NetObjects import CGraphRoot_NO, CGraphNode_NO, CGraphEdge_NO
from Lib.AgentEntity.Agent_SGItem import CAgent_SGItem
from Lib.AgentEntity.Agent_NetObject import CAgent_NO, SAP
from Lib.BoxEntity.Box_NetObject import CBox_NO, SBP
from Lib.BoxEntity.Box_SGItem import CBox_SGItem
from Lib.Common.Dummy_GItem import CDummy_GItem
from Lib.Common.GraphUtils import (getEdgeCoords, getNodeCoords, vecsFromNodes, vecsPair_withMaxAngle,
                                    rotateToRightSector, rotateToLeftSector, calcNodeMiddleLine)
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Common.Vectors import Vector2

class EGManagerMode (Flag):
    View      = auto()
    EditScene = auto()
    EditProps = auto()

class EGManagerEditMode (Flag):
    Default = auto()
    AddNode = auto()

class EGSceneSelectionMode( Enum ):
    Select = auto()
    Touch  = auto()

SGItemDesc = namedtuple( "SGItemDesc", "create_func delete_func" )

class CStorageGraph_GScene_Manager( QObject ):
    itemTouched = pyqtSignal( QGraphicsItem )
    nodeTypes_ForMiddleLine_calc = [ SGT.ENodeTypes.StoragePoint, SGT.ENodeTypes.PowerStation]

    @property
    def nxGraph(self): return graphNodeCache().nxGraph

    def __init__(self, gScene, gView):
        super().__init__()

        self.bEdgeReversing = False
        self.bGraphLoading = False
        self.agentGItems    = {}
        self.boxGItems      = {}
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
        gScene.installEventFilter(self)

        # self.gScene.setMinimumRenderSize( 3 )
        # self.gView.setViewport( QGLWidget( QGLFormat(QGL.SampleBuffers) ) )
        # self.gView.setViewport( QOpenGLWidget( ) )
        # self.gScene.setBspTreeDepth( 1 )

        self.__maxNodeID    = 0

        CNetObj_Manager.addCallback( EV.ObjCreated,       self )
        CNetObj_Manager.addCallback( EV.ObjPrepareDelete, self )
        CNetObj_Manager.addCallback( EV.ObjPropUpdated,   self )

        self.Agents_ParentGItem = CDummy_GItem()
        self.Agents_ParentGItem.setZValue( 40 )
        self.gScene.addItem( self.Agents_ParentGItem )

        self.Boxes_ParentGItem = CDummy_GItem()
        self.Boxes_ParentGItem.setZValue( 50 )
        self.gScene.addItem( self.Boxes_ParentGItem )

        self.GraphRoot_ParentGItem     = None
        self.EdgeDecorates_ParentGItem = None

        self.disabledTouchTypes = [type(None), CEdge_SGItem, CEdgeDecorate_SGItem, CAgent_SGItem, CBox_SGItem]
        self.selectionMode = EGSceneSelectionMode.Select

        self.objReloadTimer = QTimer()
        self.objReloadTimer.setInterval(500)
        self.objReloadTimer.setSingleShot( True )
        self.objReloadTimer.timeout.connect( self.updateRelationObjects )
        self.objReloadTimer.start()

        self.relationSGItems = {
                                CGraphRoot_NO : SGItemDesc(create_func=lambda x: self.init(), delete_func=lambda x: self.clear()),
                                CGraphNode_NO : SGItemDesc(create_func=self.addNode,  delete_func=self.deleteNode),
                                CGraphEdge_NO : SGItemDesc(create_func=self.addEdge,  delete_func=self.queryDeleteEdge),
                                CAgent_NO     : SGItemDesc(create_func=self.addAgent, delete_func=self.deleteAgent),
                                CBox_NO       : SGItemDesc(create_func=self.addBox,   delete_func=self.deleteBox),
                               }

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

        self.gScene.addItem( self.GraphRoot_ParentGItem )
        self.updateDecorateOnScene()

        self.initAgents_ParentGItem()
        self.initBoxes_ParentGItem()
    
    def initAgents_ParentGItem( self ):
        if self.Agents_ParentGItem.scene() is None:
            self.gScene.addItem( self.Agents_ParentGItem )

    def initBoxes_ParentGItem( self ):
        if self.Boxes_ParentGItem.scene() is None:
            self.gScene.addItem( self.Boxes_ParentGItem )

    @time_func( sMsg="Scene clear time =" )
    def clear(self):
        for box in self.boxGItems.values():
            box.setParentItem( self.Boxes_ParentGItem )

        self.nodeGItems = {}
        self.edgeGItems = {}

        self.gScene.removeItem( self.Agents_ParentGItem )
        self.gScene.removeItem( self.Boxes_ParentGItem )
        self.gScene.clear()
        self.initAgents_ParentGItem()
        self.initBoxes_ParentGItem()

        self.GraphRoot_ParentGItem     = None
        self.EdgeDecorates_ParentGItem = None

        self.gScene.update()
        
    def new(self):
        # self.clear()
        # self.init()
        # не вызываем здесь, т.к. вызовется при реакции на создание корневого элемента графа

        if graphNodeCache():
            graphNodeCache().destroy()

        createGraph_NO_Branches( nxGraph = nx.DiGraph() )
        
        self.bHasChanges = True

    def genTestGraph(self, nodes_side_count = 200, step = 2200):
        #test adding nodes
        last_node = None
        for x in range(0, nodes_side_count * step, step):
            for y in range(0, nodes_side_count * 400, 400):
                props = { SGT.SGA.x: x, SGT.SGA.y: y, SGT.SGA.nodeType : SGT.ENodeTypes.StoragePoint }
                cur_node = CGraphNode_NO( name = self.genStrNodeID(), parent = graphNodeCache().nodesNode(),
                        saveToRedis = True, props = props, ext_fields = {} )
                if last_node:
                    CGraphEdge_NO.createEdge_NetObj( nodeID_1 = cur_node.name, nodeID_2 = last_node.name, parent = graphNodeCache().edgesNode() )

                last_node = cur_node

    def load(self, sFName):
        # self.clear()
        # self.init()
        # не вызываем здесь, т.к. вызовется при реакции на создание корневого элемента графа

        self.bGraphLoading = True # For block "updateNodeMiddleLine()" on Edge creating while loading ( 5 sec overhead on "40 000 with edges" )

        if not loadGraphML_to_NetObj( sFName ):
            self.bGraphLoading = False
            return False

        self.updateMaxNodeID()

        # после создания граней перерасчитываем линии расположения мест хранения
        for nodeID, nodeGItem in self.nodeGItems.items():
            self.updateNodeMiddleLine( nodeGItem )
        
        gvFitToPage( self.gView )
        self.bHasChanges = False  # сбрасываем признак изменения сцены после загрузки

        self.bGraphLoading = False

        print( f"GraphicsItems in scene = {len(self.gScene.items())}" )
        return True

    def save( self, sFName ):
        try:
            prepared_graph = deepcopy( self.nxGraph )
            SGT.prepareGraphProps( prepared_graph, bToEnum = False )
            nx.write_graphml(prepared_graph, sFName)
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

    def updateNodeMiddleLine(self, nodeGItem):
        if nodeGItem.nodeType not in CStorageGraph_GScene_Manager.nodeTypes_ForMiddleLine_calc: return
        
        # берем смежные вершины и оставляем только те из них, для которых есть грань в edgeGItems,
        # тк в случае удаления грани или вершины они сначала удаляются из edgeGItems(nodeGItems),
        # а из графа удаляются позже и могут ещё присутствовать в графе
        NeighborsIDs = set( self.nxGraph.successors(nodeGItem.nodeID) ).union( set(self.nxGraph.predecessors(nodeGItem.nodeID)) )
        NeighborsIDs = [ ID for ID in NeighborsIDs if self.edgeGItems.get( frozenset((nodeGItem.nodeID, ID)) ) ]
        
        r_vec = calcNodeMiddleLine( self.nxGraph, nodeGItem.nodeID, NeighborsIDs )

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
            self.updateNodeMiddleLine(nodeGItem)

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
    
    #################

    def addBox( self, netObj ):
        if self.boxGItems.get ( netObj.name ): return

        boxGItem = CBox_SGItem( SGM = self, boxNetObj = netObj, parent = self.Boxes_ParentGItem )
        self.boxGItems[ netObj.name ] = boxGItem
        boxGItem.init()

        return boxGItem

    def deleteBox( self, netObj ):
        self.gScene.removeItem ( self.boxGItems[ netObj.name ] )
        del self.boxGItems[ netObj.name ]

    #################

    def addAgent( self, netObj ):
        if self.agentGItems.get ( netObj.name ): return

        agentGItem = CAgent_SGItem ( SGM=self, agentNetObj = netObj, parent=self.Agents_ParentGItem )
        self.agentGItems[ netObj.name ] = agentGItem
        agentGItem.init()

        return agentGItem

    def deleteAgent(self, netObj):
        agentGItem = self.agentGItems[ netObj.name ]
        [ child.setParentItem( self.Boxes_ParentGItem ) for child in agentGItem.childItems() if isinstance(child, CBox_SGItem) ]

        self.gScene.removeItem ( agentGItem )
        del self.agentGItems[ netObj.name ]
        del agentGItem

    #################

    def addNode( self, netObj ):
        nodeID = netObj.name
        if self.nodeGItems.get ( nodeID ): return

        nodeGItem = CNode_SGItem ( self, nodeNetObj = netObj, parent=self.GraphRoot_ParentGItem )
        self.nodeGItems[ nodeID ] = nodeGItem

        nodeGItem.init()
        nodeGItem.setFlag( QGraphicsItem.ItemIsMovable, bool (self.Mode & EGManagerMode.EditScene) )

        self.bHasChanges = True
        return nodeGItem

    def deleteNode(self, netObj):
        nodeID = netObj.name
        nodeSGItem = self.nodeGItems.get ( nodeID )
        if nodeSGItem is None: return

        [ child.setParentItem( self.Boxes_ParentGItem ) for child in nodeSGItem.childItems() if isinstance(child, CBox_SGItem) ]

        self.gScene.removeItem ( nodeSGItem )
        del self.nodeGItems[ nodeID ]
        del nodeSGItem
        self.bHasChanges = True

    #################

    def addEdge( self, netObj ):
        fsEdgeKey = frozenset( ( netObj.nxNodeID_1(), netObj.nxNodeID_2() ) )
        if self.edgeGItems.get( fsEdgeKey ) : return False

        edgeGItem = CEdge_SGItem( self, fsEdgeKey=fsEdgeKey, parent=self.GraphRoot_ParentGItem )

        edgeGItem.updatePos()
        self.edgeGItems[ fsEdgeKey ] = edgeGItem

        self.bHasChanges = True

        if not self.bGraphLoading:
            self.updateNodeMiddleLine( self.nodeGItems[ netObj.nxNodeID_1() ] )
            self.updateNodeMiddleLine( self.nodeGItems[ netObj.nxNodeID_2() ] )

        return True
    
    def addEdges_NetObj_ForSelection(self, direct = True, reverse = True):
        nodeGItems = [ n for n in self.gScene.orderedSelection if isinstance(n, CNode_SGItem) ] # выбираем из selectedItems ноды
        nodePairCount = len(nodeGItems) - 1
        
        for i in range(nodePairCount):
            nodeID_1 = nodeGItems[i].nodeID
            nodeID_2 = nodeGItems[i+1].nodeID
            if direct: #создание граней в прямом направлении
                CGraphEdge_NO.createEdge_NetObj( nodeID_1, nodeID_2, parent = graphNodeCache().edgesNode(), props=CGraphEdge_NO.def_props )

            if reverse: #создание граней в обратном направлении
                CGraphEdge_NO.createEdge_NetObj( nodeID_2, nodeID_1, parent = graphNodeCache().edgesNode(), props=CGraphEdge_NO.def_props )

            if direct == False and reverse == False: continue

            fsEdgeKey = frozenset( ( nodeID_1, nodeID_2 ) )
            edgeGItem = self.edgeGItems.get( fsEdgeKey )

            edgeGItem.update()
            edgeGItem.decorateSGItem.update()
    
    # удаление NetObj объектов определяющих грань
    def queryDeleteEdge(self, netObj):
        tKey = ( netObj.nxNodeID_1(), netObj.nxNodeID_2() )
        fsEdgeKey = frozenset( tKey )
        edgeGItem = self.edgeGItems.get( fsEdgeKey )

        if edgeGItem is None: return

        # если удаляется последняя из кратных граней, то удаляем graphicsItem который их рисовал, иначе вызываем его перерисовку
        reversedEdgeNO = edgeGItem.edgesNetObj_by_TKey[ tuple(reversed( tKey )) ]()
        if (reversedEdgeNO is None) or (reversedEdgeNO.bMarkDeleted):
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
                self.updateNodeMiddleLine( nodeGItem )

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
            CGraphEdge_NO.createEdge_NetObj( edgeGItem.nodeID_2, edgeGItem.nodeID_1, parent = graphNodeCache().edgesNode(), props=attr12 )
        
        if b21:
            CGraphEdge_NO.createEdge_NetObj( edgeGItem.nodeID_1, edgeGItem.nodeID_2, parent = graphNodeCache().edgesNode(), props=attr21 )

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

    #################

    def alignNodesVertical(self):
        nodeGItems = [ n for n in self.gScene.orderedSelection if isinstance(n, CNode_SGItem) ]
        for nodeGItem in nodeGItems:
            nodeGItem.netObj()[SGT.SGA.x] = nodeGItems[0].netObj()[SGT.SGA.x]

    def alignNodesHorisontal(self):
        nodeGItems = [ n for n in self.gScene.orderedSelection if isinstance(n, CNode_SGItem) ]
        for nodeGItem in nodeGItems:
            nodeGItem.netObj()[SGT.SGA.y] = nodeGItems[0].netObj()[SGT.SGA.y]

    #############################################################
    
    clickEvents = [ QEvent.GraphicsSceneMousePress, QEvent.GraphicsSceneMouseRelease, QEvent.GraphicsSceneMouseDoubleClick ]
    def eventFilter(self, watched, event):
        if event.type() in self.clickEvents:
            # блокирование снятия выделения с итема (челнока), когда активирован режим "Touch" при клике на пустом месте
            # или при клике по элементам сцены для которых не определена возможность "Touch"
            if self.selectionMode == EGSceneSelectionMode.Touch:
                targetGItem = self.gScene.itemAt( event.scenePos() , self.gView.transform() )
                if type( targetGItem ) in self.disabledTouchTypes:
                    event.accept()
                    return True
                                
                if event.type() == QEvent.GraphicsSceneMouseRelease:
                    self.itemTouched.emit( targetGItem )
                    self.selectionMode = EGSceneSelectionMode.Select
                
                event.accept()
                return True
    
        #########################################

        if not (self.Mode & EGManagerMode.EditScene):
            return False

        #добавление нод
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton and (self.EditMode & EGManagerEditMode.AddNode) :
                attr = {}
                attr[ SGT.SGA.nodeType ] = SGT.ENodeTypes.DummyNode
                attr[ SGT.SGA.x ] = round (self.gView.mapToScene(event.pos()).x())
                attr[ SGT.SGA.y ] = round (self.gView.mapToScene(event.pos()).y())

                CGraphNode_NO( name=self.genStrNodeID(), parent = graphNodeCache().nodesNode(), props=attr )

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
        
        event.ignore()
        return False

    def updateRelationObjects( self ):
        for agentGItem in self.agentGItems.values():
            agentGItem.updatePos()
        for boxGItem in self.boxGItems.values():
            boxGItem.updatePos()

    def moveNodes( self, nodeSGItems, x = 0, y = 0 ):
        for node in nodeSGItems:
            node.netObj().x += x
            node.netObj().y += y

    #############################################################

    @time_func( sMsg="Create scene items time", threshold=10 )
    def ObjCreated(self, netCmd=None):
        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID )

        if type(netObj) in self.relationSGItems:
            self.objReloadTimer.start()
            self.relationSGItems[ type(netObj) ].create_func( netObj )

    def ObjPrepareDelete(self, netCmd):
        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID )

        if type(netObj) in self.relationSGItems:
            self.objReloadTimer.start()
            self.relationSGItems[ type(netObj) ].delete_func( netObj )

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
            gItem = self.agentGItems[ netObj.name ]
            
            if netCmd.sPropName == SAP.angle:
                gItem.updateRotation()
            elif netCmd.sPropName in [ SAP.position, SAP.edge ]:
                gItem.updatePos()
            elif netCmd.sPropName in [ SAP.BS, SAP.status ]:
                gItem.update()

        elif isinstance( netObj, CBox_NO ):
            gItem = self.boxGItems[ netObj.name ]
            if netCmd.sPropName == SBP.address:
                gItem.updatePos()

    #############################################################
    def selectItemsByUID( self, objSet ):
        s = set()

        oldSelItems = set( self.gScene.selectedItems() )
        selItems = set()

        def select( d ):
            for item in d.values():
                if not objSet.isdisjoint( item.getNetObj_UIDs() ):
                    selItems.add( item )
                    item.setSelected( True )

        select( self.agentGItems )
        select( self.boxGItems   )
        select( self.nodeGItems  )
        select( self.edgeGItems  )

        deSelectItems = oldSelItems - selItems

        for item in deSelectItems:
            item.setSelected( False )
