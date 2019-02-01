
from Net.NetObj_Manager import CNetObj_Manager
from Net.Net_Events import ENet_Event as EV
from Net.NetCmd import CNetCmd
from Common.Graph_NetObjects import CGraphRoot_NO, CGraphNode_NO, CGraphEdge_NO

class CStorageNetObj_Adapter:
    def __init__(self):
        CNetObj_Manager.addCallback( EV.ObjCreated, self.ObjCreated )

    def ObjCreated(self, netCmd):
        netObj = CNetObj_Manager.accessObj( netCmd.Obj_UID )

        if isinstance( netObj, CGraphRoot_NO ):
            self.SGraph_Manager.nxGraph = netObj.nxGraph
        elif isinstance( netObj, CGraphNode_NO ):
            self.SGraph_Manager.addNode( netObj.name )
        elif isinstance( netObj, CGraphEdge_NO ):
            self.SGraph_Manager.addEdge( netObj.nxNodeID_1(), netObj.nxNodeID_2() )
