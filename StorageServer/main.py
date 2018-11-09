import sys

import networkx as nx

from PyQt5.QtWidgets import ( QApplication, QWidget )

from Common.SettingsManager import CSettingsManager as CSM
import Common.StrConsts as SC
from Net.NetObj import *
from Net.NetObj_Monitor import CNetObj_Monitor
from Net.NetObj_Widgets import *

from Net import NetObj_Monitor

from anytree import AnyNode, NodeMixin, RenderTree
import redis

def registerNetNodeTypes():
    reg = CNetObj_Manager.registerType
    reg( CNetObj )
    reg( CGrafRoot_NO )
    reg( CGrafNode_NO )
    reg( CGrafEdge_NO )

# загрузка графа и создание его объектов для сетевой синхронизации
def loadStorageGraph( parentBranch ):
    nxGraf  = nx.read_graphml( CSM.opt( SC.s_storage_graph_file ) )
    # nxGraf  = nx.read_graphml( "GraphML/magadanskaya_vrn.graphml" )

    Graf  = CGrafRoot_NO(name="Graf", parent=parentBranch, nxGraf=nxGraf)
    Nodes = CNetObj(name="Nodes", parent=Graf)
    Edges = CNetObj(name="Edges", parent=Graf)

    for nodeID in nxGraf.nodes():
        node = CGrafNode_NO( name=nodeID, parent=Nodes, nxNode=nxGraf.nodes()[nodeID] )

    for edgeID in nxGraf.edges():
        edge = CGrafEdge_NO( name = str(edgeID), parent=Edges, nxEdge=nxGraf.edges()[edgeID] )

    # print( RenderTree(root) )

def main():
    try:
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        r.flushdb()
    except redis.exceptions.ConnectionError as k:
        print( "[Error]: Can not connect to REDIS!" )
        return

    CSM.loadSettings()

    registerNetNodeTypes()

    rootObj  = CNetObj(name="root")
    loadStorageGraph( rootObj )
        
    CNetObj_Manager.sendAll( r )

    app = QApplication(sys.argv)

    if CSM.opt( SC.s_obj_monitor ):
        objMonitor = CNetObj_Monitor()
        objMonitor.setRootNetObj( rootObj )
        registerNetNodeWidgets( objMonitor.saNetObj_WidgetContents )
        objMonitor.show()

    app.exec_()

    CSM.saveSettings()

    r.flushdb()
