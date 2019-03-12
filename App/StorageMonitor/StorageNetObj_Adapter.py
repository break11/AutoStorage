
from PyQt5.QtCore import Qt

from Lib.Net.NetObj import CNetObj
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV
from Lib.Net.NetCmd import CNetCmd
from Lib.Common.Graph_NetObjects import CGraphRoot_NO, CGraphNode_NO, CGraphEdge_NO
from Lib.Common.Agent_NetObject import CAgent_NO
from Lib.Common.GuiUtils import time_func, Std_Model_FindItem
from Lib.Common.GraphUtils import EdgeDisplayName
from Lib.StorageViewer.Edge_SGItem import CEdge_SGItem
from Lib.StorageViewer.Node_SGItem import CNode_SGItem

class CStorageNetObj_Adapter:
    def __init__(self):
        CNetObj_Manager.addCallback( EV.ObjCreated,       self.ObjCreated )
        CNetObj_Manager.addCallback( EV.ObjPrepareDelete, self.ObjPrepareDelete )
        CNetObj_Manager.addCallback( EV.ObjPropUpdated,   self.ObjPropUpdated )

    def init( self, ViewerWindow ):
        self.SGM = ViewerWindow.SGM
        self.ViewerWindow = ViewerWindow

        ###############################################

        ##remove##
        # CNode_SGItem.propUpdate_CallBacks.append( self.nodePropChanged_From_GScene )
        # CEdge_SGItem.propUpdate_CallBacks.append( self.edgePropChanged_From_GScene )

    # def nodePropChanged_From_GScene( self, nodeID, propName, propValue ):
    #     self.__updateObjProp( "Graph/Nodes/" + nodeID, propName, propValue )

    # def edgePropChanged_From_GScene( self, tKey, propName, propValue ):
    #     self.__updateObjProp( "Graph/Edges/" + EdgeDisplayName( *tKey ), propName, propValue )

    # def __updateObjProp( self, sObjPath, propName, propValue ):
    #     netObj = CNetObj.resolvePath( CNetObj_Manager.rootObj, sObjPath )
    #     assert netObj
    #     netObj[ propName ] = propValue

    ###############################################

    @time_func( sMsg="Create scene items time", threshold=10 )
    def ObjCreated(self, netCmd=None):
        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID )
        SGM = self.SGM

        if isinstance( netObj, CGraphRoot_NO ):
            ##remove##SGM.nxGraph = netObj.nxGraph
            SGM.init()
        elif isinstance( netObj, CGraphNode_NO ):
            SGM.addNode( nodeNetObj = netObj )
        elif isinstance( netObj, CGraphEdge_NO ):
            SGM.addEdge( edgeNetObj = netObj )
        elif isinstance( netObj, CAgent_NO ):
            SGM.addAgent( agentNetObj = netObj )

    def ObjPrepareDelete(self, netCmd):
        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID )
        SGM = self.SGM

        if isinstance( netObj, CGraphRoot_NO ):
            SGM.clear()
            ##remove##SGM.nxGraph = None
        elif isinstance( netObj, CGraphNode_NO ):
            SGM.deleteNode( nodeNetObj = netObj )
        elif isinstance( netObj, CGraphEdge_NO ):
            SGM.freeEdge( edgeNetObj = netObj )
        elif isinstance( netObj, CAgent_NO ):
           SGM.deleteAgent( agentNetObj = netObj )
    
    def ObjPropUpdated(self, netCmd):
        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID )
        SGM = self.SGM
        propName  = netCmd.sPropName
        propValue = netObj[ netCmd.sPropName ]
        gItem = None

        # if SGM.nxGraph is not None: return

        if isinstance( netObj, CGraphNode_NO ):
            gItem = SGM.nodeGItems[ netObj.name ]
            gItem.updateProp( propName, propValue )

            # обновление модели свойств в окне вьювера
            if gItem != self.ViewerWindow.selectedGItem:
                SGM.updateNodeIncEdges( gItem )

        elif isinstance( netObj, CGraphEdge_NO ):
            tKey = ( netObj.nxNodeID_1(), netObj.nxNodeID_2() )
            fsEdgeKey = frozenset( tKey )

            gItem = SGM.edgeGItems[ fsEdgeKey ]
            gItem.updateProp( tKey, propName, propValue )

        elif isinstance( netObj, CAgent_NO ):
            gItem = SGM.agentGItems[ netObj.name ]
            gItem.updateProp( propName, propValue )

        # обновление модели свойств в окне вьювера
        if gItem == self.ViewerWindow.selectedGItem:
            gItem.fillPropsTable( self.ViewerWindow.objProps ) # вызовет updateNodeIncEdges для ноды внутри - из-за setData модели
