
import os
import networkx as nx
import weakref
import math
from enum import Enum, Flag, auto
from copy import deepcopy

from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
from PyQt5.QtCore import (pyqtSlot, QObject, QLineF, QPointF, QEvent, Qt)
from PyQt5.QtWidgets import ( QGraphicsItem )
from PyQt5.QtOpenGL import ( QGLWidget, QGLFormat, QGL )

from .Node_SGItem import CNode_SGItem
from .Edge_SGItem import CEdge_SGItem, CEdge_SGItem_New
from .Rail_SGItem import CRail_SGItem
from .StoragePlace_SGItem import CStoragePlace_SGItem
from .GItem_EventFilter import CGItem_EventFilter
from .GuiUtils import gvFitToPage, windowDefSettings, Std_Model_Item, EdgeDisplayName

from . import StrConsts as SC
from . import StorageGraphTypes as SGT

class EGManagerMode (Flag):
    View      = auto()
    EditScene = auto()
    EditProps = auto()

class EGManagerEditMode (Flag):
    Default = auto()
    AddNode = auto()

class CStorageGraph_GScene_Manager():
    default_Edge = {
                        SGT.s_edgeType:         'Normal',                    # type: ignore
                        SGT.s_edgeSize:         500,                         # type: ignore
                        SGT.s_highRailSizeFrom: 0,                           # type: ignore
                        SGT.s_highRailSizeTo:   0,                           # type: ignore
                        SGT.s_sensorSide:       SGT.ESensorSide.SBoth.name,  # type: ignore
                        SGT.s_widthType:        SGT.EWidthType.Narrow.name,  # type: ignore
                        SGT.s_curvature:        SGT.ECurvature.Straight.name # type: ignore
                    }

    default_Node = {  
                        SGT.s_x: 0,                                    # type: ignore
                        SGT.s_y: 0,                                    # type: ignore
                        SGT.s_nodeType: SGT.ENodeTypes.DummyNode.name, # type: ignore
                        SGT.s_containsAgent: -1,                       # type: ignore
                        SGT.s_floor_num: 0                             # type: ignore
                    }

    def __init__(self, gScene, gView):
        self.nodeGItems     = {}
        self.edgeGItems     = {}
        self.groupsByEdge   = {}
        self.edgeGItems_New = {}
        self.gScene_evI     = None
        self.nxGraph        = None

        self.bDrawBBox         = False
        self.bDrawInfoRails    = False
        self.bDrawMainRail     = False
        self.bDrawSpecialLines = False

        self.Mode           = EGManagerMode.View | EGManagerMode.EditScene | EGManagerMode.EditProps
        self.EditMode       = EGManagerEditMode.Default
        self.bHasChanges    = False

        self.gScene = gScene
        # self.gScene.setMinimumRenderSize( 3 )
        self.gView  = gView
        # self.gView.setViewport( QGLWidget( QGLFormat(QGL.SampleBuffers) ) )

        self.__maxNodeID    = 0            

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
        self.nodeGItems = {}
        self.edgeGItems = {}
        self.edgeGItems_New = {}
        self.groupsByEdge = {}
        self.gScene.clear()
        self.nxGraph = None

    def new(self):
        self.clear()
        self.init()
        
        self.nxGraph = nx.DiGraph()

        self.bHasChanges = True

    def load(self, sFName):
        self.clear()
        self.init()

        if not os.path.exists( sFName ):
            print( f"{SC.sWarning} GraphML file not found '{sFName}'!" )
            self.new()
            return False
        
        self.nxGraph  = nx.read_graphml( sFName )

        for n in self.nxGraph.nodes():
            self.addNode(n)

        self.updateMaxNodeID()

        # for e in self.nxGraph.edges():
        #     self.addEdge(*e)

        for e in self.nxGraph.edges():
            self.addEdge_New( e )

        #после создания граней перерасчитываем линии расположения мест хранения
        for nodeID, nodeGItem in self.nodeGItems.items():
            self.calcNodeMiddleLine( nodeGItem )
        
        gvFitToPage( self.gView )
        self.bHasChanges = False #сбрасываем признак изменения сцены после загрузки

        print( f"GraphicsItems on scene = {len(self.gScene.items())}" )

        return True

    def save( self, sFName ):
        nx.write_graphml(self.nxGraph, sFName)

    def setDrawInfoRails( self, bVal ):
        pass
        # self.bDrawInfoRails = bVal
        # for e, v in self.edgeGItems.items():
        #     v.setInfoRailsVisible( self.bDrawInfoRails )

    def setDrawMainRail( self, bVal ):
        self.bDrawMainRail = bVal
        for e, g in self.groupsByEdge.items():
            g.setMainRailVisible( bVal )

    def setDrawBBox( self, bVal ):
        self.bDrawBBox = bVal
        self.gScene.update()

    def setDrawSpecialLines(self, bVal):
        self.bDrawSpecialLines = bVal
        for n, v in self.nodeGItems.items():
            v.setDrawSpecialLines( bVal )
        self.gScene.update()

    #рассчет средней линии для нод
    def calcNodeMiddleLine(self, nodeGItem):        
        return
        incEdges = list( self.nxGraph.out_edges( nodeGItem.nodeID ) ) +  list( self.nxGraph.in_edges( nodeGItem.nodeID ) )
        dictEdges = {}
        for key in incEdges:
            dictEdges[frozenset( key )] = self.edgeGItems[ key ] # оставляем только некратные грани
        
        listEdges = dictEdges.values()
        AllPairEdges = [ (e1, e2) for e1 in listEdges for e2 in listEdges ]
        dictDeltaAngles={} #составляем дикт, где ключ - острый угол между гранями, значение - кортеж из двух граней

        for e1, e2 in AllPairEdges:
            delta_angle = int( abs(e1.rotateAngle() - e2.rotateAngle()) )
            delta_angle = delta_angle if delta_angle <= 180 else (360-delta_angle)
            dictDeltaAngles[ delta_angle ] = (e1, e2)
        
        if len(dictDeltaAngles) == 0:
            nodeGItem.middleLineAngle = 0
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
            dictEdges[frozenset( key )] = self.edgeGItems_New[ frozenset(key) ]

        for edgeGItem in dictEdges.values():
            edgeGItem.buildEdge()
            edgeGItem.updatePos_From_NX()

        #     # необходимо перестроить инфо-рельс, т.к. он является отдельным лайн-итемом чилдом грани
        #     edgeGItem.rebuildInfoRails()
        
        self.bHasChanges = True

        NeighborsIDs = list ( self.nxGraph.successors(nodeGItem.nodeID) ) + list ( self.nxGraph.predecessors(nodeGItem.nodeID) )
        nodeGItemsNeighbors = [ self.nodeGItems[nodeID] for nodeID in NeighborsIDs ]
        nodeGItemsNeighbors.append (nodeGItem)

        for nodeGItem in nodeGItemsNeighbors:
            self.calcNodeMiddleLine(nodeGItem)

    #  Обновление свойств графа и QGraphicsItem после редактирования полей в таблице свойств
    def updateGItemFromProps( self, gItem, stdMItem ):
        propName  = stdMItem.model().item( stdMItem.row(), 0 ).data( Qt.EditRole )
        propValue = stdMItem.data( Qt.EditRole )

        if isinstance( gItem, CNode_SGItem ):
            gItem.nxNode()[ propName ] = SGT.adjustAttrType( propName, propValue )
            gItem.init()
            gItem.updatePos_From_NX()
            gItem.updateType()
            self.updateNodeIncEdges( gItem )

        if isinstance( gItem, CEdge_SGItem_New ):
            tKey = stdMItem.data( Qt.UserRole + 1 )
            nxEdge = self.nxGraph.edges[ tKey ]
            nxEdge[ propName ] = SGT.adjustAttrType( propName, propValue )
            # gItem.rebuildInfoRails()

        self.bHasChanges = True

    #  Заполнение свойств выделенного объекта ( вершины или грани ) в QStandardItemModel
    def fillPropsForGItem( self, gItem, objProps ):
        if isinstance( gItem, CNode_SGItem ):
            objProps.setColumnCount( 2 )
            objProps.setHorizontalHeaderLabels( [ "nodeID", gItem.nodeID ] )

            for key, val in sorted( gItem.nxNode().items() ):
                rowItems = [ Std_Model_Item( key, True ), Std_Model_Item( SGT.adjustAttrType( key, val ) ) ]
                objProps.appendRow( rowItems )

        if isinstance( gItem, CEdge_SGItem_New ):
            def addNxEdgeIfExists( nodeID_1, nodeID_2, nxEdges ):
                if self.nxGraph.has_edge( nodeID_1, nodeID_2 ):
                    tE_Name = (nodeID_1, nodeID_2)
                    nxEdges[ tE_Name ] = self.nxGraph.edges[ tE_Name ]

            objProps.setColumnCount( len( gItem.childItems() ) )
            header = [ "edgeID" ]
            uniqAttrSet = set()

            nxEdges = {}
            addNxEdgeIfExists( gItem.nodeID_1, gItem.nodeID_2, nxEdges )
            addNxEdgeIfExists( gItem.nodeID_2, gItem.nodeID_1, nxEdges )

            for k,v in nxEdges.items():
                header.append( EdgeDisplayName( *k ) )
                uniqAttrSet = uniqAttrSet.union( v.keys() )

            objProps.setHorizontalHeaderLabels( header )

            for key in sorted( uniqAttrSet ):
                rowItems = []
                rowItems.append( Std_Model_Item( key, True ) )
                for k, v in nxEdges.items():
                    val = v.get( key )
                    rowItems.append( Std_Model_Item( SGT.adjustAttrType( key, val ), userData=k ) ) ## k - ключ тапл-имя грани в графе nx
                objProps.appendRow( rowItems )

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
        
    def addNode( self, nodeID, **attr ):
        if self.nodeGItems.get (nodeID): return
        if not self.nxGraph.has_node(nodeID):
            self.nxGraph.add_node ( nodeID, **attr )

        nodeGItem = CNode_SGItem ( nxGraph = self.nxGraph, nodeID = nodeID, scene = self.gScene )
        self.gScene.addItem( nodeGItem )
        self.nodeGItems[ nodeID ] = nodeGItem

        nodeGItem.init()
        nodeGItem.installSceneEventFilter( self.gScene_evI )
        nodeGItem.bDrawBBox         = self.bDrawBBox
        nodeGItem.setDrawSpecialLines( self.bDrawSpecialLines )
        nodeGItem.setFlag( QGraphicsItem.ItemIsMovable, bool (self.Mode & EGManagerMode.EditScene) )
        nodeGItem.SGM = self

        self.bHasChanges = True

    def addEdge_New( self, tupleKey ):
        edgeKey = frozenset( tupleKey )
        if self.edgeGItems_New.get( edgeKey ) : return False

        edgeGItem = CEdge_SGItem_New( self.nxGraph, edgeKey )
        edgeGItem.bDrawBBox = self.bDrawBBox
        # edgeGItem.setInfoRailsVisible( self.bDrawInfoRails )
        # edgeGroup.setMainRailVisible( self.bDrawMainRail )
        edgeGItem.updatePos_From_NX()

        self.gScene.addItem( edgeGItem )
        edgeGItem.installSceneEventFilter( self.gScene_evI )
        self.edgeGItems_New[ edgeKey ] = edgeGItem
        edgeGItem.SGM = self
        # edgeGItem.buildInfoRails()

        self.bHasChanges = True
        return True
    
    def addEdgesForSelection(self, direct = True, reverse = True):
        nodeGItems = [ n for n in self.gScene.orderedSelection if isinstance(n, CNode_SGItem) ] # выбираем из selectedItems ноды
        nodePairCount = len(nodeGItems) - 1
        
        if direct: #создание граней в прямом направлении
            for i in range(nodePairCount):
                self.addEdge( nodeGItems[i].nodeID, nodeGItems[i+1].nodeID, **self.default_Edge  )

        if reverse: #создание граней в обратном направлении
            for i in range(nodePairCount):
                self.addEdge(  nodeGItems[i+1].nodeID, nodeGItems[i].nodeID, **self.default_Edge )
    
        for nodeGItem in nodeGItems:
            self.calcNodeMiddleLine(nodeGItem)

##remove##    
    # def addEdgeToGrop(self, edgeGItem):
    #     groupKey = frozenset( (edgeGItem.nodeID_1, edgeGItem.nodeID_2) )
    #     edgeGroup = self.groupsByEdge.get( groupKey )
    #     if edgeGroup == None:
    #         edgeGroup = CRail_SGItem(groupKey=groupKey, scene=self.gScene)
    #         edgeGroup.setMainRailVisible( self.bDrawMainRail )
    #         edgeGroup.setFlags( QGraphicsItem.ItemIsSelectable )
    #         self.groupsByEdge[ groupKey ] = edgeGroup
    #         self.gScene.addItem( edgeGroup )
    #         edgeGroup.installSceneEventFilter( self.gScene_evI )

    #     edgeGroup.addToGroup( edgeGItem )

    def deleteNode(self, nodeID, bRemoveFromNX = True):
        self.nodeGItems[ nodeID ].done( bRemoveFromNX = bRemoveFromNX )
        self.gScene.removeItem ( self.nodeGItems[ nodeID ] )
        del self.nodeGItems[ nodeID ]
        self.bHasChanges = True

    def deleteEdge(self, *fsKeys : frozenset, bRemoveFromNX = True ):
        for fsKey in fsKeys:
            edgeGItem = self.edgeGItems_New.get( fsKey )
            if edgeGItem is None:
                continue
            edgeGItem.done( bRemoveFromNX = bRemoveFromNX )
            self.gScene.removeItem( edgeGItem )
            del self.edgeGItems_New[ fsKey ]

            # перерасчет средней линии для всех нод "связанных" с удаленными гранями
            for nodeID in fsKey:
                self.calcNodeMiddleLine( self.nodeGItems[ nodeID ] )

            self.bHasChanges = True


    def reverseEdge(self, nodeID_1, nodeID_2):
        if self.edgeGItems.get( (nodeID_2, nodeID_1) ) is None:
            attrs = self.edgeGItems.get( (nodeID_1, nodeID_2) ).nxEdge()
            self.deleteEdge( nodeID_1, nodeID_2 )
            self.addEdge ( nodeID_2, nodeID_1, **attrs )

    def deleteMultiEdge(self, groupKey): #удаление кратной грани
        edgeGroup = self.groupsByEdge[groupKey]
        groupChilds = edgeGroup.childItems()
        if len (groupChilds) < 2: return
        edgeGItem = groupChilds[1]
        edgeGItem.clearInfoRails()
        edgeGroup.removeFromGroup(edgeGItem)
        self.deleteEdge(edgeGItem.nodeID_1, edgeGItem.nodeID_2)

class CGItem_CreateDelete_EF(QObject): # Creation/Destruction GItems

    def __init__(self, SGraph_Manager):
        super().__init__(SGraph_Manager.gView)
        self.__SGM = SGraph_Manager
        self.__gView  = SGraph_Manager.gView
        self.__gScene = SGraph_Manager.gScene

        self.__gView.installEventFilter(self)
        self.__gView.viewport().installEventFilter(self)

    def eventFilter(self, object, event):
        if not (self.__SGM.Mode & EGManagerMode.EditScene):
            return False

        #добавление нод
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton and (self.__SGM.EditMode & EGManagerEditMode.AddNode) :
                attr = deepcopy (self.__SGM.default_Node)
                attr[ SGT.s_x ] = SGT.adjustAttrType( SGT.s_x, self.__gView.mapToScene(event.pos()).x() )
                attr[ SGT.s_y ] = SGT.adjustAttrType( SGT.s_y, self.__gView.mapToScene(event.pos()).y() )
                self.__SGM.addNode( self.__SGM.genStrNodeID(), **attr )

                ##TODO: разобраться и починить ув-е размера сцены при добавление элементов на ее краю
                # self.__gScene.setSceneRect( self.__gScene.itemsBoundingRect() )
                # self.__gView.setSceneRect( self.__gView.scene().sceneRect() )

                event.accept()
                return True

        #удаление итемов
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Delete:

            for item in self.__gScene.selectedItems():

                if isinstance( item, CNode_SGItem ):
                    incEdges = list( self.__SGM.nxGraph.out_edges( item.nodeID ) ) +  list( self.__SGM.nxGraph.in_edges( item.nodeID ) )
                    fsKeys = set( [ frozenset(s) for s in incEdges ] )
                    self.__SGM.deleteEdge( *fsKeys )
                    self.__SGM.deleteNode( item.nodeID )            

                # if isinstance( item, CEdge_SGItem_New ):
                #     self.__SGM.deleteEdge( item.fsEdgeKey )

            
            event.accept()
            return True
        
        return False