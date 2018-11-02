import sys

import networkx as nx

from PyQt5.QtWidgets import ( QApplication, QWidget )

from Common.SettingsManager import CSettingsManager as CSM
from Net.NetObj_Monitor import CNetObj_Monitor
from Net.NetObj import *
from Net.NetObj_Widgets import *

from anytree import AnyNode, NodeMixin, RenderTree

def main():
    # CSM.loadSettings()

    app = QApplication(sys.argv)


    nxGraf  = nx.read_graphml( "GraphML/test.graphml" )
    # nxGraf  = nx.read_graphml( "GraphML/magadanskaya_vrn.graphml" )

    # root2 = AnyNode(id="0", name="root2")

    registerNetNodeTypes()
    registerNetNodeWidgets()

    root  = CNetObj(name="root")
    Graf  = CGraf_NO(name="Graf", parent=root)
    Nodes = CNetObj(name="Nodes", parent=Graf)
    Edges = CNetObj(name="Edges", parent=Graf)

    for nodeID in nxGraf.nodes():
        node = CGrafNode_NO(name=nodeID, parent=Nodes)

    for edgeID in nxGraf.edges():
        edge = CGrafEdge_NO(name = str(edgeID), parent=Edges)

    print( RenderTree(root) )

    objMonitor = CNetObj_Monitor()
    objMonitor.setRootNetObj( root )
    objMonitor.show()

    app.exec_()

    # CSM.saveSettings()
