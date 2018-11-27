import networkx as nx
from anytree import AnyNode, NodeMixin, RenderTree
import redis
import os

from PyQt5.QtWidgets import ( QApplication, QWidget )

from Common.SettingsManager import CSettingsManager as CSM
from Common.BaseApplication import *
import Common.StrConsts as SC
from Net.NetObj import *
from Net.NetObj_Manager import *
from Net.NetObj_Monitor import CNetObj_Monitor
from Net.NetObj_Widgets import *

from Common.Graf_NetObjects import *
from .def_settings import *

# загрузка графа и создание его объектов для сетевой синхронизации
def loadStorageGraph( parentBranch ):

    sFName = CSM.rootOpt( s_storage_graph_file, default=s_storage_graph_file__default )
    if not os.path.exists( sFName ):
        print( f"[Warning]: GraphML file not found '{sFName}'!" )
        return

    nxGraf  = nx.read_graphml( sFName )
    # не используем атрибуты для значений по умолчанию для вершин и граней, поэтому сносим их из свойств графа
    # как и следует из документации новые ноды не получают этот список атрибутов, это просто кеш
    # при создании графа через загрузку они появляются, при создании чистого графа ( nx.Graph() ) нет
    del nxGraf.graph["node_default"]
    del nxGraf.graph["edge_default"]

    # nxGraf  = nx.read_graphml( "GraphML/magadanskaya_vrn.graphml" )

    Graf  = CGrafRoot_NO( name="Graf", parent=parentBranch, nxGraf=nxGraf )
    Nodes = CNetObj(name="Nodes", parent=Graf)
    Edges = CNetObj(name="Edges", parent=Graf)

    for nodeID in nxGraf.nodes():
        node = CGrafNode_NO( name=nodeID, parent=Nodes )
        # node = CGrafNode_NO( name=nodeID, parent=Nodes, nxNode=nxGraf.nodes()[nodeID] )

    for edgeID in nxGraf.edges():
        n1 = edgeID[0]
        n2 = edgeID[1]
        edge = CGrafEdge_NO( name = GraphEdgeName( n1, n2 ), nxNodeID_1 = n1, nxNodeID_2 = n2, parent = Edges )

    # print( RenderTree(root) )

    # Graf  = CNetObj( name="Graf", parent=parentBranch )
    # Nodes = CNetObj(name="Nodes", parent=Graf)
    # Edges = CNetObj(name="Edges", parent=Graf)
    # CNetObj( name="nodeID", parent=Nodes )
    # CNetObj( name="nodeID", parent=Nodes )
    # CNetObj( name="nodeID", parent=Nodes )
    # CNetObj( name="nodeID", parent=Nodes )
    # CNetObj( name="nodeID", parent=Edges )
    # CNetObj( name="nodeID", parent=Edges )
    # CNetObj( name="nodeID", parent=Edges )
    # CNetObj( name="nodeID", parent=Edges )

def main():    
    registerNetObjTypes()

    app = CBaseApplication(sys.argv)
    app.bIsServer = True    
    if not app.init( default_settings = serverDefSet ): return -1
    
    loadStorageGraph( CNetObj_Manager.rootObj )
    app.objMonitor.clearView()

    app.exec_() # главный цикл сообщений Qt

    app.done()
    return 0
