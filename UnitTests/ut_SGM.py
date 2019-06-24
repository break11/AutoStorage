#!/usr/bin/python3.7
import unittest

import sys
import os
import networkx as nx
import math

sys.path.append( os.path.abspath(os.curdir)  )

# from PyQt5.QtWidgets import QGraphicsView, QWidget
# from PyQt5.QtWidgets import QApplication

from Lib.StorageViewer.StorageGraph_GScene_Manager import CStorageGraph_GScene_Manager
from Lib.Common import StorageGraphTypes as SGT
from Lib.Common.GraphUtils import loadGraphML_File
sDir = "./GraphML/"

# Dummy-классы для имитиции окружения StorageGraph_GScene_Manager

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
            self.addNode( nodeID )

        ####
        for tKey in self.nxGraph.edges():
            self.addEdge( tKey )

    def addNode(self, nodeID):
        dummyNodeItem = CNode_SGItem_Dummy(nodeID)
        self.nodeGItems[nodeID] = dummyNodeItem
        try:
            if self.nxGraph.nodes()[nodeID][SGT.s_nodeType] == SGT.ENodeTypes.StorageSingle.name:
                dummyNodeItem.nodeType = SGT.ENodeTypes.StorageSingle
        except:
            pass

    def addEdge(self, tKey):
        self.edgeGItems[ frozenset(tKey) ] = True

    def calcNodeMiddleLine(self, dummyNodeItem):
        CStorageGraph_GScene_Manager.calcNodeMiddleLine(self, dummyNodeItem)


SGM = CSGM_Dummy ( sDir + "test_storage_rotation.graphml" )

for dummyNodeItem in SGM.nodeGItems.values():
    SGM.calcNodeMiddleLine( dummyNodeItem )

class Test_SGM_Funcs(unittest.TestCase):

    def test_calcNodeMiddleLine(self):


        self.assertTrue(    math.isclose( SGM.nodeGItems["n0"].middleLineAngle, 225.0, abs_tol=1e-9 )    )
        self.assertTrue(    math.isclose( SGM.nodeGItems["2"].middleLineAngle,  360.0, abs_tol=1e-9 )    )
        self.assertTrue(    math.isclose( SGM.nodeGItems["5"].middleLineAngle,  270.0, abs_tol=1e-9 )    )
        self.assertTrue(    math.isclose( SGM.nodeGItems["8"].middleLineAngle,  315.0, abs_tol=1e-9 )    )
        self.assertTrue(    math.isclose( SGM.nodeGItems["11"].middleLineAngle, 315.0, abs_tol=1e-9 )    )
        self.assertTrue(    math.isclose( SGM.nodeGItems["14"].middleLineAngle, 360.0, abs_tol=1e-9 )    )
        self.assertTrue(    math.isclose( SGM.nodeGItems["19"].middleLineAngle, 251.565051177078, abs_tol=1e-9 )    )
        self.assertTrue(    math.isclose( SGM.nodeGItems["21"].middleLineAngle, 247.499999999999, abs_tol=1e-9 )    )
        
        self.assertEqual(   SGM.nodeGItems["nLU"].middleLineAngle, None    )

        # удаление грани
        ###############################################################
        del SGM.edgeGItems[ frozenset( ("14", "15") ) ]

        SGM.calcNodeMiddleLine( SGM.nodeGItems["14"] )
        self.assertTrue(    math.isclose( SGM.nodeGItems["14"].middleLineAngle,  324.4623222080256, abs_tol=1e-9 )    )


        # удаление ноды
        #! удаление ноды из графа происходит после перерасчета средней линии
        ###############################################################
        del SGM.nodeGItems["12"]
        del SGM.edgeGItems[ frozenset( ("11", "12") ) ]

        SGM.calcNodeMiddleLine( SGM.nodeGItems["11"] )
        self.assertTrue(    math.isclose( SGM.nodeGItems["11"].middleLineAngle, 341.565051177078, abs_tol=1e-9 )    )
        SGM.nxGraph.remove_node("12")

        ###############################################################
        del SGM.nodeGItems["10"]
        del SGM.edgeGItems[ frozenset( ("11", "10") ) ]

        SGM.calcNodeMiddleLine( SGM.nodeGItems["11"] )
        self.assertTrue(    math.isclose( SGM.nodeGItems["11"].middleLineAngle, 0.0, abs_tol=1e-9 )    )
        SGM.nxGraph.remove_node("10")

        ###############################################################
        del SGM.nodeGItems["9"]
        del SGM.edgeGItems[ frozenset( ("9", "8") ) ]

        SGM.calcNodeMiddleLine( SGM.nodeGItems["8"] )
        self.assertTrue(    math.isclose( SGM.nodeGItems["8"].middleLineAngle, 263.6400056854672, abs_tol=1e-9 )    )
        SGM.nxGraph.remove_node("9")


        # добавление ноды
        ###############################################################
        SGM.nxGraph.add_node( "9", x = 1800, y = 3200 )
        SGM.addNode( "9" )
        SGM.nxGraph.add_edge( "8", "9" )
        SGM.addEdge( ("9", "8") )

        SGM.calcNodeMiddleLine( SGM.nodeGItems["8"] )
        self.assertTrue(    math.isclose( SGM.nodeGItems["8"].middleLineAngle,  315.0, abs_tol=1e-9 )    )

if __name__ == "__main__":
    unittest.main()
