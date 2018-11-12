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

import threading

class CNetCMDReader( threading.Thread ):
    def __init__(self, netLink, bAppWorking):
        super().__init__()
        self.r = netLink
        self.receiver = netLink.pubsub()
        self.receiver.subscribe('net-cmd')
        self.bAppWorking = bAppWorking
    
    def run(self):
        while self.bAppWorking.value:
            # print("Hello from the thread!", self.bAppWorking.value)
            msg = self.receiver.get_message(False, 0.5)
            if msg: print( msg )

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
    class bAppWorking: pass
    bAppWorking.value = True

    try:
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        r.flushdb()
    except redis.exceptions.ConnectionError as k:
        print( "[Error]: Can not connect to REDIS!" )
        return

    CNetObj_Manager.connect()
    CNetObj_Manager.disconnect()

    CSM.loadSettings()

    registerNetNodeTypes()

    rootObj  = CNetObj(name="root")
    loadStorageGraph( rootObj )
        
    CNetObj_Manager.sendAll( r )

    app = QApplication(sys.argv)

    # if CSM.opt( SC.s_obj_monitor ):
    objMonitor = CNetObj_Monitor()
    objMonitor.setRootNetObj( rootObj )
    registerNetNodeWidgets( objMonitor.saNetObj_WidgetContents )
    objMonitor.show()

    netReader = CNetCMDReader( r, bAppWorking )
    # netReader.setDaemon(True)
    netReader.start()

    app.exec_()

    CSM.saveSettings()

    r.flushdb()
    bAppWorking.value = False
