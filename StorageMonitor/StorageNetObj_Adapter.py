
from Net.NetObj_Manager import CNetObj_Manager
from Net.Net_Events import ENet_Event as EV
from Net.NetCmd import CNetCmd
from Common.Graph_NetObjects import CGraphRoot_NO, CGraphNode_NO, CGraphEdge_NO
from Common.GuiUtils import time_func

class CStorageNetObj_Adapter:
    def __init__(self):
        CNetObj_Manager.addCallback( EV.ObjCreated, self.ObjCreated )
        CNetObj_Manager.addCallback( EV.ObjPrepareDelete, self.ObjPrepareDelete )

    @time_func( sMsg="Create scene items time", threshold=10 )
    def ObjCreated(self, netCmd=None):
        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID )
        SGM = self.SGraph_Manager

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
        SGM = self.SGraph_Manager

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
            