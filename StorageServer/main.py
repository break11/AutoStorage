import sys

import networkx as nx

from PyQt5.QtWidgets import ( QApplication, QWidget )

from Common.SettingsManager import CSettingsManager as CSM
from Common.NetObj_Monitor import CNetObj_Monitor
from Common.NetObj import *

from anytree import AnyNode, NodeMixin, RenderTree
# from mainwindow import CSMD_MainWindow

def main():
    # CSM.loadSettings()

    app = QApplication(sys.argv)


    # nxGraf  = nx.read_graphml( "GraphML/test.graphml" )
    nxGraf  = nx.read_graphml( "GraphML/magadanskaya_vrn.graphml" )

    # root2 = AnyNode(id="0", name="root2")

    root  = CNetObj(name="root")
    Graf  = CGraf_NO(name="Graf", parent=root)
    Nodes = CNetObj(name="Nodes", parent=Graf)
    Edges = CNetObj(name="Edges", parent=Graf)

    for nodeID in nxGraf.nodes():
        node = CNode_NO(name=nodeID, parent=Nodes)
        # for k,v in nxGraf.nodes().items():
        #     prop = CNetObj( name=k,  )

    for edgeID in nxGraf.edges():
        print( str(edgeID) )
        edge = CEdge_NO(name = str(edgeID), parent=Edges)

    print( RenderTree(root) )



    objMonitor = CNetObj_Monitor()
    objMonitor.setRootNetObj( root )
    objMonitor.show()

    app.exec_()

    # CSM.saveSettings()
