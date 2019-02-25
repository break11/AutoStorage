
from PyQt5.QtCore import Qt

from Lib.Net.NetObj import CNetObj
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Net.NetCmd import CNetCmd
from Lib.Common.Graph_NetObjects import CGraphRoot_NO, CGraphNode_NO, CGraphEdge_NO
from Lib.Common.GuiUtils import time_func, Std_Model_FindItem, EdgeDisplayName

class CStorageNetObj_Adapter:
    def __init__(self):
        CNetObj_Manager.addCallback( EV.ObjCreated,       self.ObjCreated )
        CNetObj_Manager.addCallback( EV.ObjPrepareDelete, self.ObjPrepareDelete )
        CNetObj_Manager.addCallback( EV.ObjPropUpdated,   self.ObjPropUpdated )

    def init( self, ViewerWindow ):
        self.SGM = ViewerWindow.SGM
        self.ViewerWindow = ViewerWindow
        self.ViewerWindow.nodePropChanged_From_TableProps = self.nodePropChanged_From_GScene_TableProps
        self.ViewerWindow.edgePropChanged_From_TableProps = self.edgePropChanged_From_GScene_TableProps


    def nodePropChanged_From_GScene_TableProps( self, nodeID, propName, propValue ):
        self.__updateObjProp( "Graph/Nodes/" + nodeID, propName, propValue )

    def edgePropChanged_From_GScene_TableProps( self, tKey, propName, propValue ):
        self.__updateObjProp( "Graph/Edges/" + EdgeDisplayName( *tKey ), propName, propValue )

    def __updateObjProp( self, sObjPath, propName, propValue ):
        netObj = CNetObj.resolvePath( CNetObj_Manager.rootObj, sObjPath )
        assert netObj
        netObj[ propName ] = propValue

    @time_func( sMsg="Create scene items time", threshold=10 )
    def ObjCreated(self, netCmd=None):
        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID )
        SGM = self.SGM

        if isinstance( netObj, CGraphRoot_NO ):
            SGM.nxGraph = netObj.nxGraph
            SGM.init()
        elif isinstance( netObj, CGraphNode_NO ):
            SGM.addNode( netObj.name )
        elif isinstance( netObj, CGraphEdge_NO ):
            SGM.addEdge( frozenset( (netObj.nxNodeID_1(), netObj.nxNodeID_2()) ) )
            SGM.calcNodeMiddleLine( SGM.nodeGItems[ netObj.nxNodeID_1() ] )
            SGM.calcNodeMiddleLine( SGM.nodeGItems[ netObj.nxNodeID_2() ] )

    def ObjPrepareDelete(self, netCmd):
        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID )
        SGM = self.SGM

        if isinstance( netObj, CGraphRoot_NO ):
            SGM.clear()
            SGM.nxGraph = None
        elif isinstance( netObj, CGraphNode_NO ):
            if SGM.nxGraph is not None:
                SGM.deleteNode( netObj.name )
        elif isinstance( netObj, CGraphEdge_NO ):
            if SGM.nxGraph is not None:
                # грань удалится из nxGraph в netObj
                # если удаляется последняя из кратных граней, то удаляем graphicsItem который их рисовал, иначе вызываем его перерисовку
                fsEdgeKey = frozenset( ( netObj.nxNodeID_1(), netObj.nxNodeID_2() ) )
                if not SGM.nxGraph.has_edge( netObj.nxNodeID_2(), netObj.nxNodeID_1() ):
                    SGM.deleteEdge( fsEdgeKey )
                else:
                    SGM.edgeGItems[ fsEdgeKey ].update()
                    self.ViewerWindow.StorageMap_Scene_SelectionChanged()
    
    def ObjPropUpdated(self, netCmd):
        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID )
        SGM = self.SGM
        propName  = netCmd.sPropName
        propValue = netObj[ netCmd.sPropName ]
        gItem = None

        # if SGM.nxGraph is not None: return

        if isinstance( netObj, CGraphNode_NO ):
            gItem = SGM.nodeGItems[ netObj.name ]
            SGM.updateNodeProp( gItem, propName, propValue )

            # обновление модели свойств в окне вьювера
            if gItem == self.ViewerWindow.selectedGItem:
                stdItem_PropName = Std_Model_FindItem( pattern=propName, model=self.ViewerWindow.objProps, col=0 )
                if stdItem_PropName is not None:
                    stdItem_PropValue = self.ViewerWindow.objProps.item( stdItem_PropName.row(), 1 )
                    stdItem_PropValue.setData( propValue, Qt.EditRole )

        elif isinstance( netObj, CGraphEdge_NO ):
            tKey = ( netObj.nxNodeID_1(), netObj.nxNodeID_2() )
            fsEdgeKey = frozenset( tKey )
            gItem = SGM.edgeGItems[ fsEdgeKey ]
            SGM.updateEdgeProp( gItem, tKey, propName, propValue )

            # обновление модели свойств в окне вьювера
            if gItem == self.ViewerWindow.selectedGItem:
                stdItem_PropName = Std_Model_FindItem( pattern=propName, model=self.ViewerWindow.objProps, col=0 )
                if stdItem_PropName is None: return

                row = stdItem_PropName.row()

                def __updateEdgeProp( col, tKey, val ):
                    stdItem_PropValue = self.ViewerWindow.objProps.item( row, col )
                    if stdItem_PropValue is not None:
                        if stdItem_PropValue.data( Qt.UserRole + 1 ) == tKey:
                            stdItem_PropValue.setData( val, Qt.EditRole )

                __updateEdgeProp( 1, tKey, propValue )
                __updateEdgeProp( 2, tKey, propValue )
