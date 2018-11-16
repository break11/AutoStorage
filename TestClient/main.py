import networkx as nx

from PyQt5.QtWidgets import ( QApplication, QWidget )

from Common.SettingsManager import CSettingsManager as CSM
import Common.StrConsts as SC
from Net.NetObj import *
from Net.NetObj_Manager import *
from Net.NetObj_Monitor import CNetObj_Monitor
from Net.NetObj_Widgets import *

from anytree import AnyNode, NodeMixin, RenderTree
import redis
import os

import threading

class CNetCMDReader( threading.Thread ):
    def __init__(self, netLink):
        super().__init__()
        self.r = netLink
        self.receiver = netLink.pubsub()
        self.receiver.subscribe('net-cmd')
        self.bStop = False

    def terminate(self):
        print( "test" )
    
    def run(self):
        while not self.bStop:
            # print("Hello from the thread!", self.bAppWorking.value)
            msg = self.receiver.get_message(False, 0.5)
            if msg: print( msg )

def registerNetObjTypes():
    reg = CNetObj_Manager.registerType
    reg( CNetObj )
    reg( CGrafRoot_NO )
    reg( CGrafNode_NO )
    reg( CGrafEdge_NO )

# загрузка графа и создание его объектов для сетевой синхронизации
# def loadStorageGraph( parentBranch ):

#     sFName = CSM.opt( SC.s_storage_graph_file )
#     if not os.path.exists( sFName ):
#         print( f"[Warning]: GraphML file not found '{sFName}'!" )
#         return

#     nxGraf  = nx.read_graphml( sFName )
#     # nxGraf  = nx.read_graphml( "GraphML/magadanskaya_vrn.graphml" )

#     Graf  = CGrafRoot_NO(name="Graf", parent=parentBranch, nxGraf=nxGraf)
#     Nodes = CNetObj(name="Nodes", parent=Graf)
#     Edges = CNetObj(name="Edges", parent=Graf)

#     for nodeID in nxGraf.nodes():
#         node = CGrafNode_NO( name=nodeID, parent=Nodes, nxNode=nxGraf.nodes()[nodeID] )

#     for edgeID in nxGraf.edges():
#         edge = CGrafEdge_NO( name = str(edgeID), parent=Edges, nxEdge=nxGraf.edges()[edgeID] )

#     # print( RenderTree(root) )

def main():
    CSM.loadSettings()
    
    registerNetObjTypes()

    # CNetObj_Manager.clientID = -1 # признак того, что сервер
    if not CNetObj_Manager.connect(): return
    CNetObj_Manager.init()

    # loadStorageGraph( CNetObj_Manager.rootObj )
        
    CNetObj_Manager.sendAll()

    app = QApplication(sys.argv)

    if CNetObj_Monitor.enaledInOptions():
        objMonitor = CNetObj_Monitor()
        objMonitor.setRootNetObj( CNetObj_Manager.rootObj )
        registerNetNodeWidgets( objMonitor.saNetObj_WidgetContents )
        objMonitor.show()

    netReader = CNetCMDReader( CNetObj_Manager.redisConn )
    netReader.setDaemon(True)
    netReader.start()

    app.exec_()

    CSM.saveSettings()

    netReader.bStop = True

    CNetObj_Manager.disconnect()
    # удаление объектов после дисконнекта, чтобы в сеть НЕ попали команды удаления объектов ( для других клиентов )
    CNetObj_Manager.rootObj.clearChildren() 
