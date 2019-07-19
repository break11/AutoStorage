#!/usr/bin/python3.7
import unittest

import sys
import os
import networkx as nx
import math
import weakref

sys.path.append( os.path.abspath(os.curdir)  )

# from PyQt5.QtWidgets import QGraphicsView, QWidget
# from PyQt5.QtWidgets import QApplication

from Lib.StorageViewer.StorageGraph_GScene_Manager import CStorageGraph_GScene_Manager
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Common.Graph_NetObjects import loadGraphML_to_NetObj, graphNodeCache
from Lib.Common import StorageGraphTypes as SGT
from Lib.Common.GraphUtils import loadGraphML_File
sDir = "./GraphML/"

# Dummy-классы для имитиции окружения StorageGraph_GScene_Manager

class CNode_SGItem_Dummy:
    def __init__(self, nodeNetObj):
        self.nodeType = SGT.ENodeTypes.NoneType
        self.middleLineAngle = None
        self.netObj = weakref.ref( nodeNetObj )

    def setMiddleLineAngle(self, fVal):
        self.middleLineAngle = fVal

    @property
    def nodeID( self ): return self.netObj().name

class CSGM_Dummy:
    def __init__(self, sFName):
        self.nodeGItems = {}
        self.edgeGItems = {}

        CNetObj_Manager.initRoot()
        loadGraphML_to_NetObj( sFName = sFName, bReload = False)
        self.graphRootNode = graphNodeCache()

        for nodeNetObj in self.graphRootNode().nodesNode().children:
            self.addNode( nodeNetObj )

        for tKey in self.nxGraph.edges():
            self.addEdge( tKey )

    @property
    def nxGraph(self): return self.graphRootNode().nxGraph

    def addNode(self, nodeNetObj):
        dummyNodeItem = CNode_SGItem_Dummy(nodeNetObj)
        nodeID = nodeNetObj.name
        self.nodeGItems[nodeID] = dummyNodeItem
        try:
            sType = self.nxGraph.nodes()[nodeID][SGT.s_nodeType]
            dummyNodeItem.nodeType = SGT.ENodeTypes.fromString( sType )
        except:
            dummyNodeItem.nodeType = SGT.ENodeTypes.NoneType

    def addEdge(self, tKey):
        #пока для тестирования достаточно чтобы дикт граней был просто заполнен
        self.edgeGItems[ frozenset(tKey) ] = True

    def __getattr__(self, name):
        #для перенаправления вызова функции "name" к функции CStorageGraph_GScene_Manager
        SGM_Func = CStorageGraph_GScene_Manager.__getattribute__(CStorageGraph_GScene_Manager, name)
        return lambda *args, **kwargs : SGM_Func(self, *args, **kwargs)


SGM = CSGM_Dummy ( sDir + "test_storage_rotation.graphml" )


class Test_SGM_Funcs(unittest.TestCase):

    def test_updateNodeMiddleLine(self):

        for dummyNodeItem in SGM.nodeGItems.values():
            SGM.updateNodeMiddleLine( dummyNodeItem )

        # StorageSingle
        self.assertTrue(    math.isclose( SGM.nodeGItems["n0"].middleLineAngle, 225.0, abs_tol=1e-9 )    )
        self.assertTrue(    math.isclose( SGM.nodeGItems["2"].middleLineAngle,  360.0, abs_tol=1e-9 )    )
        self.assertTrue(    math.isclose( SGM.nodeGItems["5"].middleLineAngle,  270.0, abs_tol=1e-9 )    )
        self.assertTrue(    math.isclose( SGM.nodeGItems["8"].middleLineAngle,  315.0, abs_tol=1e-9 )    )
        self.assertTrue(    math.isclose( SGM.nodeGItems["11"].middleLineAngle, 315.0, abs_tol=1e-9 )    )
        self.assertTrue(    math.isclose( SGM.nodeGItems["14"].middleLineAngle, 360.0, abs_tol=1e-9 )    )
        self.assertTrue(    math.isclose( SGM.nodeGItems["19"].middleLineAngle, 251.565051177078, abs_tol=1e-9 )    )
        self.assertTrue(    math.isclose( SGM.nodeGItems["21"].middleLineAngle, 247.499999999999, abs_tol=1e-9 )    )
        
        # ServiceStation
        self.assertTrue(    math.isclose( SGM.nodeGItems["24"].middleLineAngle, 360.0, abs_tol=1e-9 )    )
        self.assertTrue(    math.isclose( SGM.nodeGItems["27"].middleLineAngle, 180.0, abs_tol=1e-9 )    )
        self.assertTrue(    math.isclose( SGM.nodeGItems["29"].middleLineAngle, 270.0, abs_tol=1e-9 )    )
        self.assertTrue(    math.isclose( SGM.nodeGItems["33"].middleLineAngle,  90.0, abs_tol=1e-9 )    )

        # NoneType
        self.assertEqual(   SGM.nodeGItems["nLU"].middleLineAngle, None    )

        # удаление граней из SGM.edgeGItems, пересчет средней линии
        del SGM.edgeGItems[ frozenset( ("9",  "8") ) ]
        SGM.updateNodeMiddleLine( SGM.nodeGItems[ "8" ] )
        self.assertTrue(    math.isclose( SGM.nodeGItems["8"].middleLineAngle,  263.6400056854672, abs_tol=1e-9 )    )

        del SGM.edgeGItems[ frozenset( ("16",  "8") ) ]
        SGM.updateNodeMiddleLine( SGM.nodeGItems[ "8" ] )
        self.assertTrue(    math.isclose( SGM.nodeGItems["8"].middleLineAngle,  300.9637565320735, abs_tol=1e-9 )    )

if __name__ == "__main__":
    unittest.main()
