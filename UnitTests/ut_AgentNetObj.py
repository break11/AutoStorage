#!/usr/bin/python3.7

import unittest
import sys
import os
from copy import deepcopy

sys.path.append( os.path.abspath(os.curdir)  )

from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.NetObj import CNetObj
import Lib.Common.GraphUtils as GU
from Lib.GraphEntity.Graph_NetObjects import loadGraphML_to_NetObj, graphNodeCache
import Lib.AgentEntity.Agent_NetObject as ANO
from Lib.Common.SerializedList import CStrList

sDir = "./GraphML/"

CNetObj_Manager.initRoot()
loadGraphML_to_NetObj( sFName = sDir + "magadanskaya.graphml", bReload = False)
CNetObj_Manager.rootObj.queryObj( ANO.s_Agents, CNetObj ) #type:ignore
graphRootNode = graphNodeCache()


nxGraph        = graphRootNode().nxGraph

tEdgeKey_1_2   = ("1", "2")
lEdgeKey_1_2   = list( tEdgeKey_1_2 )
strList_EdgeKey_1_2 = CStrList.fromTuple( tEdgeKey_1_2 )

tEdgeKey_2_1   = ("2", "1")
lEdgeKey_2_1   = list( tEdgeKey_2_1 )
strList_EdgeKey_2_1 = CStrList.fromTuple( tEdgeKey_2_1 )

tEdgeKey_2_3   = ("2", "3")
strList_EdgeKey_2_3 = CStrList.fromTuple( tEdgeKey_2_3 )

edgeSize_1_2   = GU.edgeSize( nxGraph, tEdgeKey_1_2 )
edgeSize_2_1   = GU.edgeSize( nxGraph, tEdgeKey_2_1 )

Route_1        = ["1", "2", "3", "4", "5", "6"]
strRoute_1     = ",".join( Route_1 )

Route_2        = ["2", "3", "4", "5", "6"]
strRoute_2     = ",".join( Route_2 )

Route_3        = ["3", "4", "5", "6"]

class CTestAgentNetObjFuncs(unittest.TestCase):

    def test_applyRoute(self):
        agentNO = ANO.queryAgentNetObj( "111" )
        
        ###########################  CASE 1  #####################################
        # Челнок стоит на первой грани в маршруте, на позиции 0.
        # Маршрут должен примениться без изменений, позиция и грань челнока не меняются.

        agentNO.edge = strList_EdgeKey_1_2
        agentNO.position = 0
        agentNO.route = CStrList()

        test_route = agentNO.applyRoute( deepcopy(Route_1) )

        self.assertEqual( test_route, Route_1 )
        self.assertEqual( agentNO.route.toString(), strRoute_1 )
        self.assertEqual( agentNO.edge, strList_EdgeKey_1_2 )
        self.assertEqual( agentNO.position, 0 )

        ###########################  CASE 2A  #####################################
        # Челнок стоит на первой грани в маршруте, на позиции менее(равно) 50% от длины.
        # Маршрут должен примениться без изменений, позиция и грань челнока не меняются.
        agentNO.edge = strList_EdgeKey_1_2
        position = round (edgeSize_1_2 * 0.5)
        agentNO.position = position
        agentNO.route = CStrList()

        test_route = agentNO.applyRoute( deepcopy(Route_1) )

        self.assertEqual( test_route, Route_1 )
        self.assertEqual( agentNO.route.toString(), strRoute_1 )
        self.assertEqual( agentNO.edge, strList_EdgeKey_1_2 )
        self.assertEqual( agentNO.position, position )

        ###########################  CASE 2B  #####################################
        # Челнок стоит на первой грани в маршруте, на позиции менее(равно) 50% от длины, маршрут из двух нод.
        # Маршрут должен примениться без изменений, позиция и грань челнока не меняются.
        agentNO.edge = strList_EdgeKey_1_2
        position = round (edgeSize_1_2 * 0.5)
        agentNO.position = position
        agentNO.route = CStrList()

        test_route = agentNO.applyRoute( deepcopy(lEdgeKey_1_2) )

        self.assertEqual( test_route, lEdgeKey_1_2 )
        self.assertEqual( agentNO.route(), lEdgeKey_1_2 )
        self.assertEqual( agentNO.edge, strList_EdgeKey_1_2 )
        self.assertEqual( agentNO.position, position )

        ###########################  CASE 3A  #####################################
        # Челнок стоит на первой грани в маршруте, на позиции более 50% от длины.
        # Из маршрута удаляется первая нода, челнок переставляется на первую грань нового маршрута, позиция 0.
        agentNO.edge = strList_EdgeKey_1_2
        agentNO.position = edgeSize_1_2
        agentNO.route = CStrList()

        test_route = agentNO.applyRoute( deepcopy(Route_1) )

        self.assertEqual( test_route, Route_2 )
        self.assertEqual( agentNO.route.toString(), strRoute_2 )
        self.assertEqual( agentNO.edge, strList_EdgeKey_2_3 )
        self.assertEqual( agentNO.position, 0 )

        ###########################  CASE 3B  #####################################
        # Челнок стоит на первой грани в маршруте, на позиции более 50% от длины, маршрут из двух нод.
        # Считаем, что челнок уже на конечной ноде маршрута.
        
        agentNO.edge = strList_EdgeKey_1_2
        position = round (edgeSize_1_2 * 0.51)
        agentNO.position = position
        agentNO.route = CStrList()

        test_route = agentNO.applyRoute( deepcopy(lEdgeKey_1_2) )

        self.assertEqual( test_route, None )
        self.assertTrue ( agentNO.route.isEmpty() )
        self.assertEqual( agentNO.edge, strList_EdgeKey_1_2 )
        self.assertEqual( agentNO.position, position )

        ###########################  CASE 4A  #####################################
        # Челнок стоит на грани, кратной первой грани в маршруте, на позиции более(равно) 50% от длины.
        # Маршрут должен примениться без изменений, челнок переставляется на первую грань маршрута, позиция = (длина грани - исходная позиция).
        agentNO.edge = strList_EdgeKey_2_1
        position = round (edgeSize_2_1 * 0.5)
        agentNO.position = position
        agentNO.route = CStrList()

        test_route = agentNO.applyRoute( deepcopy(Route_1) )

        self.assertEqual( test_route, Route_1 )
        self.assertEqual( str( agentNO.route ), strRoute_1 )
        self.assertEqual( agentNO.edge, strList_EdgeKey_1_2 )
        self.assertEqual( agentNO.position, (edgeSize_2_1 - position) )

        ###########################  CASE 4B  #####################################
        # Челнок стоит на грани, кратной первой грани в маршруте, на позиции более(равно) 50% от длины, маршрут из двух нод.
        # Маршрут должен примениться без изменений, челнок переставляется на первую грань маршрута, позиция = (длина грани - исходная позиция).
        agentNO.edge = strList_EdgeKey_2_1
        position = round (edgeSize_2_1 * 0.5)
        agentNO.position = position
        agentNO.route = CStrList()

        test_route = agentNO.applyRoute( deepcopy(lEdgeKey_1_2) )

        self.assertEqual( test_route, lEdgeKey_1_2 )
        self.assertEqual( agentNO.route(),  lEdgeKey_1_2 )
        self.assertEqual( agentNO.edge, strList_EdgeKey_1_2 )
        self.assertEqual( agentNO.position, (edgeSize_2_1 - position) )

        ###########################  CASE 5A  #####################################
        # Челнок стоит на грани, кратной первой грани в маршруте, на позиции менее 50% от длины.
        # Из маршрута удаляется первая нода, челнок переставляется на первую грань нового маршрута, позиция 0.
        agentNO.edge = strList_EdgeKey_2_1
        position = round( edgeSize_2_1 * 0.49 )
        agentNO.position = position
        agentNO.route = CStrList()

        test_route = agentNO.applyRoute( deepcopy(Route_1) )

        self.assertEqual( test_route, Route_2 )
        self.assertEqual( agentNO.route.toString(), strRoute_2 )
        self.assertEqual( agentNO.edge, strList_EdgeKey_2_3 )
        self.assertEqual( agentNO.position, 0 )

        ###########################  CASE 5B  #####################################
        # Челнок стоит на грани, кратной первой грани в маршруте, на позиции менее 50% от длины, маршрут из двух нод.
        # Считаем, что челнок уже на конечной ноде маршрута. Челнок переставляется на кратную грань, позиция = (длина грани - исходная позиция).
        agentNO.edge = strList_EdgeKey_2_1
        position = round( edgeSize_2_1 * 0.49 )
        agentNO.position = position
        agentNO.route = CStrList()

        test_route = agentNO.applyRoute( deepcopy(lEdgeKey_1_2) )

        self.assertEqual( test_route, None )
        self.assertTrue( agentNO.route.isEmpty() )
        self.assertEqual( agentNO.edge, strList_EdgeKey_1_2 )
        self.assertEqual( agentNO.position, (edgeSize_2_1 - position) )

        ###########################  CASE 6  #####################################
        # Челнок стоит на грани, первая нода которой совпадает с первой нодой в маршруте, на позиции менее 50% от длины.
        # Маршрут не меняется, челнок переставляется на первую грань маршрута, позиция 0.
        agentNO.edge = strList_EdgeKey_2_1
        position = round( edgeSize_2_1 * 0.49 )
        agentNO.position = position
        agentNO.route = CStrList()

        test_route = agentNO.applyRoute( deepcopy(Route_2) )
        self.assertEqual( test_route, Route_2 )
        self.assertEqual( agentNO.route.toString(), strRoute_2 )
        self.assertEqual( agentNO.edge, strList_EdgeKey_2_3 )
        self.assertEqual( agentNO.position, 0 )

        ###########################  CASE 7  #####################################
        # Челнок стоит на грани, первая нода которой совпадает с первой нодой в маршруте, на позиции более(равно) 50% от длины.
        # В начало маршрута добавляется вторая нода текущей грани, челнок переставляется на кратную грань, позиция = (длина грани - исходная позиция).
        agentNO.edge = strList_EdgeKey_2_1
        position = round( edgeSize_2_1 * 0.5 )
        agentNO.position = position
        agentNO.route = CStrList()

        test_route = agentNO.applyRoute( deepcopy(Route_2) )
        self.assertEqual( test_route, Route_1 )
        self.assertEqual( agentNO.route.toString(), strRoute_1 )
        self.assertEqual( agentNO.edge, strList_EdgeKey_1_2 )
        self.assertEqual( agentNO.position, (edgeSize_2_1 - position) )

        ###########################  CASE 8A  #####################################
        # Маршрут из одной ноды. Нода - первая нода грани, на которой стоит челнок. Позиция менее 50% от длины.
        # Считаем, что челнок уже на конечной ноде маршрута. Челнок переставляется на кратную грань, позиция = (длина грани - исходная позиция).
        agentNO.edge = strList_EdgeKey_1_2
        position = round( edgeSize_1_2 * 0.49 )
        agentNO.position = position
        agentNO.route = CStrList()

        test_route = agentNO.applyRoute( [ tEdgeKey_1_2[0] ] )
        self.assertEqual( test_route, None )
        self.assertTrue( agentNO.route.isEmpty() )
        self.assertEqual( agentNO.edge, strList_EdgeKey_2_1 )
        self.assertEqual( agentNO.position, (edgeSize_1_2 - position) )

        ###########################  CASE 8B  #####################################
        # Маршрут из одной ноды. Нода - первая нода грани, на которой стоит челнок. Позиция более(равно) 50% от длины.
        # В начало маршрута добавляется вторая нода текущей грани. Челнок переставляется на кратную грань, позиция = (длина грани - исходная позиция).
        agentNO.edge = strList_EdgeKey_1_2
        position = round( edgeSize_1_2 * 0.5 )
        agentNO.position = position
        agentNO.route = CStrList()

        test_route = agentNO.applyRoute( [ tEdgeKey_1_2[0] ] )
        self.assertEqual( test_route, lEdgeKey_2_1 )
        self.assertEqual( agentNO.route(), lEdgeKey_2_1 )
        self.assertEqual( agentNO.edge, strList_EdgeKey_2_1 )
        self.assertEqual( agentNO.position, (edgeSize_1_2 - position) )

        ###########################  CASE 8C  #####################################
        # Маршрут из одной ноды. Нода - вторая нода грани, на которой стоит челнок. Позиция менее (равно) 50% от длины.
        # Маршрут - это текущая грань. Позиция и грань не меняются.
        agentNO.edge = strList_EdgeKey_1_2
        position = round( edgeSize_1_2 * 0.5 )
        agentNO.position = position
        agentNO.route = CStrList()

        test_route = agentNO.applyRoute( [ tEdgeKey_1_2[1] ] )
        self.assertEqual( test_route, lEdgeKey_1_2 )
        self.assertEqual( agentNO.route(), lEdgeKey_1_2 )
        self.assertEqual( agentNO.edge, strList_EdgeKey_1_2 )
        self.assertEqual( agentNO.position, position )

        ###########################  CASE 8D  #####################################
        # Маршрут из одной ноды. Нода - вторая нода грани, на которой стоит челнок. Позиция более 50% от длины.
        # Считаем, что челнок уже на конечной ноде маршрута.
        agentNO.edge = strList_EdgeKey_1_2
        position = round( edgeSize_1_2 * 0.51 )
        agentNO.position = position
        agentNO.route = CStrList()

        test_route = agentNO.applyRoute( [ tEdgeKey_1_2[1] ] )
        self.assertEqual( test_route, None )
        self.assertTrue( agentNO.route.isEmpty() )
        self.assertEqual( agentNO.edge, strList_EdgeKey_1_2 )
        self.assertEqual( agentNO.position, position )

        ###########################  CASE 9  #####################################
        # Челнок стоит на грани, вторая нода которой совпадает с первой нодой в маршруте, на позиции менее(равно) 50% от длины.
        # В начало маршрута добавляется первая нода текущей грани, грань и позиция челнока не меняются.
        agentNO.edge = strList_EdgeKey_1_2
        position = round( edgeSize_1_2 * 0.5 )
        agentNO.position = position
        agentNO.route = CStrList()

        test_route = agentNO.applyRoute( deepcopy(Route_2) )
        self.assertEqual( test_route, Route_1 )
        self.assertEqual( agentNO.route.toString(), strRoute_1 )
        self.assertEqual( agentNO.edge, strList_EdgeKey_1_2 )
        self.assertEqual( agentNO.position, position )

        ###########################  CASE 10  #####################################
        # Челнок стоит на грани, вторая нода которой совпадает с первой нодой в маршруте, на позиции более 50% от длины.
        # Маршрут не меняется, челнок переставляется на первую грань маршрута, позиция 0.
        agentNO.edge = strList_EdgeKey_1_2
        position = round( edgeSize_1_2 * 0.51 )
        agentNO.position = position
        agentNO.route = CStrList()

        test_route = agentNO.applyRoute( deepcopy(Route_2) )
        self.assertEqual( test_route, Route_2 )
        self.assertEqual( agentNO.route.toString(), strRoute_2 )
        self.assertEqual( agentNO.edge, strList_EdgeKey_2_3 )
        self.assertEqual( agentNO.position, 0 )

        ###########################  CASE 11  #####################################
        # Маршрут - пустой лист.
        agentNO.edge = strList_EdgeKey_1_2
        agentNO.position = 0
        agentNO.route = CStrList()

        test_route = agentNO.applyRoute( [] )
        self.assertEqual( test_route, None )
        self.assertTrue( agentNO.route.isEmpty() )
        self.assertEqual( agentNO.edge, strList_EdgeKey_1_2 )
        self.assertEqual( agentNO.position, 0 )

        ###########################  CASE 12  #####################################
        # Челнок стоит на грани, ноды которой не присутствуют в начале маршрута.
        agentNO.edge = strList_EdgeKey_1_2
        agentNO.position = 0
        agentNO.route = CStrList()

        with self.assertRaises( AssertionError ):
            agentNO.applyRoute( Route_3 )

        ###########################  CASE 13  #####################################
        # Челнок вне графа.
        agentNO.edge = CStrList()
        agentNO.position = 0
        agentNO.route = CStrList()

        with self.assertRaises( AssertionError ):
            agentNO.applyRoute( deepcopy(Route_1) )


        agentNO.destroy()

if __name__ == "__main__":
    unittest.main()