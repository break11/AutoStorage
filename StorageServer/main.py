import networkx as nx

from PyQt5.QtWidgets import ( QApplication, QWidget )

from Common.SettingsManager import CSettingsManager as CSM
from Common.BaseApplication import CBaseApplication
import Common.StrConsts as SC
from Net.NetObj import *
from Net.NetObj_Manager import *
from Net.NetObj_Monitor import CNetObj_Monitor
from Net.NetObj_Widgets import *

from anytree import AnyNode, NodeMixin, RenderTree
import redis
import os

def registerNetObjTypes():
    reg = CNetObj_Manager.registerType
    reg( CNetObj )
    reg( CGrafRoot_NO )
    reg( CGrafNode_NO )
    reg( CGrafEdge_NO )

# загрузка графа и создание его объектов для сетевой синхронизации
def loadStorageGraph( parentBranch ):

    sFName = CSM.opt( SC.s_storage_graph_file )
    if not os.path.exists( sFName ):
        print( f"[Warning]: GraphML file not found '{sFName}'!" )
        return

    nxGraf  = nx.read_graphml( sFName )
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
    registerNetObjTypes()

    app = CBaseApplication(sys.argv)
    app.bIsServer = True    
    if not app.init(): return -1
    
    loadStorageGraph( CNetObj_Manager.rootObj )
    app.objMonitor.clearView()

    CNetObj_Manager.sendAll()

    app.exec_() # главный цикл сообщений Qt

    app.done()
    return 0
