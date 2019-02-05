
from Net.NetObj_Manager import CNetObj_Manager
from Net.Net_Events import ENet_Event as EV
from Net.NetCmd import CNetCmd
from Common.Graph_NetObjects import CGraphRoot_NO, CGraphNode_NO, CGraphEdge_NO

class CStorageNetObj_Adapter:
    def __init__(self):
        CNetObj_Manager.addCallback( EV.ObjCreated, self.ObjCreated )
        CNetObj_Manager.addCallback( EV.ObjPrepareDelete, self.ObjPrepareDelete )

    def ObjCreated(self, netCmd):
        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID )
        SGM = self.SGraph_Manager

        if isinstance( netObj, CGraphRoot_NO ):
            SGM.nxGraph = netObj.nxGraph
        elif isinstance( netObj, CGraphNode_NO ):
            SGM.addNode( netObj.name )
        elif isinstance( netObj, CGraphEdge_NO ):
            SGM.addEdge( netObj.nxNodeID_1(), netObj.nxNodeID_2() )
            for nodeGItem in [ SGM.nodeGItems[nodeID] for nodeID in [netObj.nxNodeID_1(), netObj.nxNodeID_2()] ]:
                SGM.calcNodeMiddleLine(nodeGItem)

    def ObjPrepareDelete(self, netCmd):
        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID )
        SGM = self.SGraph_Manager

        if isinstance( netObj, CGraphRoot_NO ):
            SGM.clear()
            SGM.nxGraph = None
        # elif isinstance( netObj, CGraphNode_NO ):
        #     if SGM.nxGraph:
        #         SGM.deleteNode( netObj.name, bRemoveFromNX = False )
        # elif isinstance( netObj, CGraphEdge_NO ):
        #     groupKey = frozenset( (netObj.nxNodeID_1(), netObj.nxNodeID_2()) )
            
        #     SGM.deleteEdge( netObj.nxNodeID_1(), netObj.nxNodeID_2(), bRemoveFromNX = False )
        #     if not len( SGM.groupsByEdge[ groupKey ].childItems() ):
        #         SGM.deleteEdgeGroup( groupKey )

            
