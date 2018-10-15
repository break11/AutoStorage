
import networkx as nx

from PyQt5.QtWidgets import (QGraphicsItemGroup )
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)

from Node_SGItem import *
from Edge_SGItem import *
from GItem_EventFilter import *
from GuiUtils import *
import xml.etree.ElementTree as ET

graphML_attr_types = { "widthType"        : str,
                       "edgeSize"         : float,
                       "highRailSizeFrom" : float,
                       "highRailSizeTo"   : float,
                       "curvature"        : str,
                       "edgeType"         : str,
                       "sensorSide"       : str,
                       "chargeSide"       : str,
                       "containsAgent"    : int,
                       "floor_num"        : int,
                       "x"                : float,
                       "y"                : float,
                       "nodeType"         : str,
                       "storageType"      : str,
                       "name"             : str }


class CGraphXmlAttr():
    __known_types = { 'int'   : int,
                      'float' : float,
                      'string': str }
    __known_attrs = {}
                 
    def load( self, sFName ):
        tree = ET.parse( sFName )
        root = tree.getroot()

        for child in root.findall( "key" ):
            self.__known_attrs[ child.get("attr.name") ] = child.get("attr.type")
            print( child.get("attr.name"), child.get("attr.type") )

    def clear( self ):
        self.__known_attrs = {}

    def getAttrType( self, sAttrName ):
        sAttrType = self.__known_attrs.get( sAttrName )
        # if sAttrType is None: return str

        attrType = self.__known_types.get( sAttrType )
        # if attrType is None: return str
        return attrType

class CStorageGraf_GScene_Manager():
    gScene = None
    gView = None
    nxGraf  = None
    bDrawBBox = False
    graphXmlAttr = CGraphXmlAttr()
    # nodeGItems: typing.Dict[str, CGrafNodeItem]   = {}  # nodeGItems = {} # onlu for mypy linter
    # edgeGItems: typing.Dict[tuple, CGrafEdgeItem] = {}  # nodeGItems = {} # onlu for mypy linter
    nodeGItems = {}
    edgeGItems = {}
    groupsByEdge = {}

    def __init__(self, gScene, gView):
        self.gScene = gScene
        self.gView  = gView

    def clear( self ):
        self.nodeGItems = {}
        self.edgeGItems = {}
        self.groupsByEdge = {}
        self.gScene.clear()
        self.graphXmlAttr.clear()

    def load( self, sFName ):
        self.clear()
        
        self.graphXmlAttr.load( sFName )
        self.nxGraf  = nx.read_graphml( sFName )
        evI = CGItem_EventFilter()
        self.gScene.addItem( evI )

        for n in self.nxGraf.nodes():
            nodeGItem = CNode_SGItem( self.nxGraf, n )
            nodeGItem.setPos( self.nxGraf.node[ n ]['x'], self.nxGraf.node[ n ]['y'] )
            self.gScene.addItem( nodeGItem )
            nodeGItem.installSceneEventFilter( evI )
            nodeGItem.setZValue( 20 )
            self.nodeGItems[ n ] = nodeGItem

        for e in self.nxGraf.edges():
            edgeGItem = CEdge_SGItem( self.nxGraf, *e )
            edgeGItem.setPos( self.nxGraf.node[ e[0] ]['x'], self.nxGraf.node[ e[0] ]['y'] )
            self.edgeGItems[ e ] = edgeGItem
            
            edgeKey = frozenset( [ e[0], e[1] ] )
            edgeGroup = self.groupsByEdge.get( edgeKey )
            if edgeGroup == None:
                edgeGroup = QGraphicsItemGroup()
                edgeGroup.setFlags( QGraphicsItem.ItemIsSelectable )
                self.groupsByEdge[ edgeKey ] = edgeGroup
                self.gScene.addItem( edgeGroup )
                edgeGroup.installSceneEventFilter( evI )

            edgeGroup.addToGroup( edgeGItem )
            edgeGItem.installSceneEventFilter( evI )

        self.gScene.setSceneRect( self.gScene.itemsBoundingRect() )
        
        gvFitToPage( self.gView )
        # self.gScene.addRect( self.gScene.sceneRect() )


    def save( self, sFName ):
        nx.write_graphml(self.nxGraf, sFName)

    def setDrawBBox( self, bVal ):
        for n, v in self.nodeGItems.items():
            v.bDrawBBox = bVal

        for e, v in self.edgeGItems.items():
            v.bDrawBBox = bVal

    #  Обновление свойств графа и QGraphicsItem после редактирования полей в таблице модели свойств
    def updateGItemFromProps( self, gItem, stdMItem ):
        if isinstance( gItem, CNode_SGItem ):
            propName  = stdMItem.model().item( stdMItem.row(), 0 ).data( Qt.EditRole )
            propValue = stdMItem.data( Qt.EditRole )
            gItem.nxNode()[ propName ] = propValue
            nodeID = gItem.nodeID

            nodeGItem = self.nodeGItems[ nodeID ]
            x = nodeGItem.nxNode()['x']
            y = nodeGItem.nxNode()['y']
            nodeGItem.setPos( x, y )
            
            incEdges = list( self.nxGraf.out_edges( nodeID ) ) +  list( self.nxGraf.in_edges( nodeID ) )
            for key in incEdges:
                edgeGItem = self.edgeGItems[ key ]
                edgeGItem.buildEdge()

                # Граням выходящим из узла обновляем позицию, входящим - нет
                if gItem.nodeID == key[0]:
                    edgeGItem.setPos( x, y )

                groupItem = self.groupsByEdge[ frozenset( key ) ]

                # https://bugreports.qt.io/browse/QTBUG-25974
                # В связи с ошибкой в Qt группа не меняет свой размер при изменении геометрии чилдов
                # поэтому приходится пересоздавать группу, убирая элементы и занося их в нее вновь 
                groupItem.removeFromGroup( edgeGItem )
                groupItem.addToGroup( edgeGItem )

        if isinstance( gItem, QGraphicsItemGroup ):
            propName  = stdMItem.model().item( stdMItem.row(), 0 ).data( Qt.EditRole )
            propValue = stdMItem.data( Qt.EditRole )

            print( gItem.childItems()[ stdMItem.column() - 1 ].edgeName(), propName, propValue, self.graphXmlAttr.getAttrType( propName ) )

            propValue = (graphML_attr_types[ propName ] )( propValue )
            gItem.childItems()[ stdMItem.column() - 1 ].nxEdge()[ propName ] = propValue

    #  Заполнение свойств выделенного объекта ( вершины или грани ) в QStandardItemModel
    def fillPropsForGItem( self, gItem, objProps ):
        if isinstance( gItem, CNode_SGItem ):
            objProps.setColumnCount( 2 )
            objProps.setHorizontalHeaderLabels( [ "nodeID", gItem.nodeID ] )

            for key, val in sorted( gItem.nxNode().items() ):
                rowItems = [ Std_Model_Item( key, True ), Std_Model_Item( val ) ]
                objProps.appendRow( rowItems )

        if isinstance( gItem, QGraphicsItemGroup ):
            objProps.setColumnCount( len( gItem.childItems() ) )
            header = [ "edgeID" ]
            uniqAttrSet = set()
            for eGItem in gItem.childItems():
                eGItem.edgeName()
                header.append( eGItem.edgeName() )
                uniqAttrSet = uniqAttrSet.union( eGItem.nxEdge().keys() )

            objProps.setHorizontalHeaderLabels( header )

            for key in sorted( uniqAttrSet ):
                rowItems = []
                rowItems.append( Std_Model_Item( key, True ) )
                for eGItem in gItem.childItems():
                    val = eGItem.nxEdge().get( key )
                    rowItems.append( Std_Model_Item( val ) )
                objProps.appendRow( rowItems )
        
    # def __del__(self):
        # print( "del CGrafSceneManager", self.QGraphicsScene )
