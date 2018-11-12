import sys

import networkx as nx

from PyQt5.QtWidgets import ( QApplication, QWidget )

from Common.SettingsManager import CSettingsManager as CSM
from Net.NetObj import *
from Net.NetObj_Monitor import CNetObj_Monitor
from Net.NetObj_Widgets import *

from Net import NetObj_Monitor

from anytree import AnyNode, NodeMixin, RenderTree

def main():
    # CSM.loadSettings()

    app = QApplication(sys.argv)

    nxGraf  = nx.read_graphml( "GraphML/test.graphml" )
    # nxGraf  = nx.read_graphml( "GraphML/magadanskaya_vrn.graphml" )

    # root2 = AnyNode(id="0", name="root2")

    registerNetNodeTypes()

    root  = CNetObj(name="root")

    Graf  = CGrafRoot_NO(name="Graf", parent=root, nxGraf=nxGraf)
    Nodes = CNetObj(name="Nodes", parent=Graf)
    Edges = CNetObj(name="Edges", parent=Graf)

    for nodeID in nxGraf.nodes():
        node = CGrafNode_NO( name=nodeID, parent=Nodes, nxNode=nxGraf.nodes()[nodeID] )

    for edgeID in nxGraf.edges():
        edge = CGrafEdge_NO(name = str(edgeID), parent=Edges, nxEdge=nxGraf.edges()[edgeID])

    print( RenderTree(root) )

    objMonitor = CNetObj_Monitor()
    objMonitor.setRootNetObj( root )

    registerNetNodeWidgets( objMonitor.saNetObj_WidgetContents )

    objMonitor.show()

    # print(  [_ for _ in sys.modules if 'netobj' in _.lower()]   )

    app.exec_()

    # CSM.saveSettings()
