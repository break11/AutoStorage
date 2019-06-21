#!/usr/bin/python3.7
import unittest

import sys
import os
import networkx as nx

sys.path.append( os.path.abspath(os.curdir)  )

# from PyQt5.QtWidgets import QGraphicsView, QWidget
# from PyQt5.QtWidgets import QApplication

from Lib.StorageViewer.StorageGraph_GScene_Manager import CStorageGraph_GScene_Manager
from Lib.Common import StorageGraphTypes as SGT
from Lib.Common.GraphUtils import loadGraphML_File
sDir = "./GraphML/"

class CNode_SGItem_Dummy:
    def __init__(self, nodeID):
        self.nodeID = nodeID
        self.nodeType = SGT.ENodeTypes.NoneType
        self.middleLineAngle = None

    def setMiddleLineAngle(self, fVal):
        self.middleLineAngle = fVal

class CSGM_Dummy:
    def __init__(self, sFName):
        self.nodeGItems     = {}
        self.edgeGItems     = {}

        self.nxGraph = loadGraphML_File(sFName)

        ####
        for nodeID in self.nxGraph.nodes():
            dummyNodeItem = CNode_SGItem_Dummy(nodeID)
            self.nodeGItems[nodeID] = dummyNodeItem
            try:
                if self.nxGraph.nodes()[nodeID][SGT.s_nodeType] == SGT.ENodeTypes.StorageSingle.name:
                    dummyNodeItem.nodeType = SGT.ENodeTypes.StorageSingle
            except:
                pass

        ####
        for tKey in self.nxGraph.edges():
            self.edgeGItems[ frozenset(tKey) ] = True

    def calcNodeMiddleLine(self, dummyNodeItem):
        CStorageGraph_GScene_Manager.calcNodeMiddleLine(self, dummyNodeItem)


SGM = CSGM_Dummy ( sDir + "test_storage_rotation.graphml" )

for dummyNodeItem in SGM.nodeGItems.values():
    SGM.calcNodeMiddleLine( dummyNodeItem )
    # print ( dummyNodeItem.nodeID, dummyNodeItem.middleLineAngle )