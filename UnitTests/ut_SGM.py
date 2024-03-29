#!/usr/bin/python3.7
import unittest

import sys
import os
import networkx as nx
import math
import weakref
# import gc

sys.path.append( os.path.abspath(os.curdir)  )

from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.StorageViewer.StorageGraph_GScene_Manager import CStorageGraph_GScene_Manager
import Lib.GraphEntity.Graph_NetObjects as GNO
from Lib.GraphEntity import StorageGraphTypes as SGT

from Lib.Common.TreeNodeCache import CTreeNodeCache

sDir = "./GraphML/"

CNetObj_Manager.initRoot()

# Dummy-классы для имитиции окружения StorageGraph_GScene_Manager
class CNode_SGItem_Dummy:
    @property
    def nodeType( self ): return self.netObj().nodeType

    def __init__(self, nodeNetObj):
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

        CNetObj_Manager.rootObj.queryObj( GNO.s_Graph, GNO.CGraphRoot_NO )
        GNO.loadGraphML_to_NetObj( sFName = sFName )

        for nodeNetObj in GNO.graphNodeCache().nodesNode().children:
            self.addNode( nodeNetObj )

        for tKey in self.nxGraph.edges():
            self.addEdge( tKey )

    @property
    def nxGraph(self): return GNO.graphNodeCache().nxGraph

    def addNode(self, nodeNetObj):
        dummyNodeItem = CNode_SGItem_Dummy(nodeNetObj)
        nodeID = nodeNetObj.name
        self.nodeGItems[nodeID] = dummyNodeItem

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

        # StoragePoint
        self.assertTrue(    math.isclose( SGM.nodeGItems["n0"].middleLineAngle, 45.0,  abs_tol=1e-9 )    )
        self.assertTrue(    math.isclose( SGM.nodeGItems["2"].middleLineAngle,  360.0, abs_tol=1e-9 )    )
        self.assertTrue(    math.isclose( SGM.nodeGItems["5"].middleLineAngle,  270.0, abs_tol=1e-9 )    )
        self.assertTrue(    math.isclose( SGM.nodeGItems["8"].middleLineAngle,  315.0, abs_tol=1e-9 )    )
        self.assertTrue(    math.isclose( SGM.nodeGItems["11"].middleLineAngle, 315.0, abs_tol=1e-9 )    )
        self.assertTrue(    math.isclose( SGM.nodeGItems["14"].middleLineAngle, 360.0, abs_tol=1e-9 )    )
        self.assertTrue(    math.isclose( SGM.nodeGItems["19"].middleLineAngle, 251.565051177078, abs_tol=1e-9 )    )
        self.assertTrue(    math.isclose( SGM.nodeGItems["21"].middleLineAngle, 247.499999999999, abs_tol=1e-9 )    )
        
        # PowerStation
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
