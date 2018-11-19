import networkx as nx

from PyQt5.QtWidgets import ( QApplication, QWidget )
from PyQt5.QtCore import ( QTimer )

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
import queue

class CNetCMDReader( threading.Thread ):
    def __init__(self, netLink, q):
        super().__init__()
        self.setDaemon(True)
        self.r = netLink
        self.receiver = netLink.pubsub()
        self.receiver.subscribe('net-cmd')
        self.__bIsRunning = False
        self.__bStop = False
        self.q = q
    
    def run(self):
        self.__bStop = False
        self.__bIsRunning = True
        while self.__bIsRunning:
            # print( threading.get_ident() )
            # print("Hello from the thread!", self.bAppWorking.value)
            msg = self.receiver.get_message(False, 0.5)
            if msg:
                print( msg )
                self.q.put( msg )

            if self.__bStop: self.__bIsRunning = False

    def stop(self):
        self.__bStop = True
        while self.__bIsRunning: pass
        

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

class CBaseApplication( QApplication ):
    def __init__(self, argv ):
        super().__init__( argv )
        self.timer = QTimer()
        self.timer.timeout.connect( self.onTick )
        self.timer.start()

    def onTick(self):
        print( "tick" )



def main():
    # print( threading.get_ident() )

    CSM.loadSettings()
    
    registerNetObjTypes()

    # CNetObj_Manager.clientID = -1 # признак того, что сервер
    if not CNetObj_Manager.connect(): return
    CNetObj_Manager.init()

    # loadStorageGraph( CNetObj_Manager.rootObj )
        
    CNetObj_Manager.sendAll()

    app = CBaseApplication(sys.argv)

    if CNetObj_Monitor.enaledInOptions():
        objMonitor = CNetObj_Monitor()
        objMonitor.setRootNetObj( CNetObj_Manager.rootObj )
        registerNetNodeWidgets( objMonitor.saNetObj_WidgetContents )
        objMonitor.show()

    q = queue.Queue()
    netReader = CNetCMDReader( CNetObj_Manager.redisConn, q )
    netReader.start()

    # while not q.empty(): process( q )
    # process 

    app.exec_()

    CSM.saveSettings()

    netReader.stop()

    CNetObj_Manager.disconnect()
    # удаление объектов после дисконнекта, чтобы в сеть НЕ попали команды удаления объектов ( для других клиентов )
    CNetObj_Manager.rootObj.clearChildren() 
