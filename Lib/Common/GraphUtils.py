
import math
import networkx as nx
import os
import re
import random

from Lib.GraphEntity import StorageGraphTypes as SGT
from Lib.GraphEntity.StorageGraphTypes import SGA
from Lib.Common.Vectors import Vector2
from Lib.Common.StrConsts import SC

def edgesListFromNodes( nodesList ):
    edgesList = []
    for i in range( len(nodesList)-1 ):
        edgesList.append( ( nodesList[ i ], nodesList[ i+1 ]) )
    return edgesList

def nodesList_FromStr( nodes_str ):
    pattern = " ,|,| |:|-"
    l = re.split(pattern, nodes_str)

    return l if len(l) > 1 else []

def edgeSize(nxGraph,  tKey ):
    return nxGraph.edges()[ tKey ][ SGA.edgeSize ]

def nodeProp(nxGraph, nodeID, sPropName):
    try:
        return nxGraph.nodes()[ nodeID ][ sPropName ]
    except KeyError:
        print( f"{SC.sError} Node {nodeID} has not prop with name {sPropName}!" )
        return None

def nodeType(nxGraph, nodeID):
    return nodeProp( nxGraph, nodeID, SGA.nodeType )

def nodeChargePort(nxGraph, nodeID):
    return nodeProp( nxGraph, nodeID, SGA.chargePort )

def nodeByPos( nxGraph, tKey, pos, allowOffset=50 ):
    l = edgeSize( nxGraph, tKey )
    if pos < l / 2:
        if pos > allowOffset: return None
        nodeID = tKey[0]
    else:
        if l-pos > allowOffset: return None
        nodeID = tKey[1]

    return nodeID

def randomNodes( nxGraph, _nodeTypes, count = 1, allowDuplicates = False ):
    nodes = [ nodeID for nodeID in nxGraph.nodes() if nodeType( nxGraph, nodeID ) in _nodeTypes ]
    assert allowDuplicates or len(nodes) >= count, f"Not enought unique nodes in the Graph for choosing {count} random nodes of {_nodeTypes} types."
    
    selected = []
    while len( selected ) < count:
        nodeID = random.choice( nodes )
        if allowDuplicates or nodeID not in selected:
            selected.append( nodeID )

    return selected

def isOnNode( nxGraph, tKey, pos, allowOffset=50, _nodeID=None, _nodeTypes=None ):
    nodeID = nodeByPos( nxGraph, tKey, pos, allowOffset )

    if nodeID is None: return False

    bR = True if _nodeID is None else nodeID==_nodeID

    bR = bR and ( True if _nodeTypes is None else nodeType( nxGraph, nodeID ) in _nodeTypes )

    return bR

def tEdgeKeyFromStr( edge_str ):
    return tuple( nodesList_FromStr( edge_str) )

def tEdgeKeyToStr( tEdgeKey, bReversed = False ):    
    return f"{tEdgeKey[0]} {tEdgeKey[1]}"

def getEdgeCoords (nxGraph, tEdgeKey):
    nodeID_1, nodeID_2 = tEdgeKey[0], tEdgeKey[1]

    if not nxGraph.has_edge( nodeID_1, nodeID_2 ):
        return

    x1 = nxGraph.nodes()[ nodeID_1 ][SGA.x]
    y1 = nxGraph.nodes()[ nodeID_1 ][SGA.y]
    
    x2 = nxGraph.nodes()[ nodeID_2 ][SGA.x]
    y2 = nxGraph.nodes()[ nodeID_2 ][SGA.y]

    return x1, y1, x2, y2

def getNodeCoords (nxGraph, nodeID):

    if not nxGraph.has_node( nodeID ):
        return

    x = nxGraph.nodes()[ nodeID ][SGA.x]
    y = nxGraph.nodes()[ nodeID ][SGA.y]
    
    return x, y

def getAgentAngle(nxGraph, tEdgeKey, agent_angle):
    edgeCoords = getEdgeCoords( nxGraph, tEdgeKey )
    if edgeCoords is None: return agent_angle, False

    x1, y1, x2, y2 = edgeCoords

    edge_vec = Vector2( x2 - x1, - (y2 - y1) ) #берём отрицательное значение "y" тк, значения по оси "y" увеличиваются по направлению вниз
    
    railType = nxGraph.edges()[ tEdgeKey ][ SGA.widthType ]
    
    agent_vec = Vector2.fromAngle( math.radians( agent_angle ) )
    
    #Если рельс широкий, используем для рассчёта повернутый на -90 градусов вектор грани,
    #так как направление "вперёд" для челнока на широком рельсе это вектор челнока, повернутый на +90 градусов
    #поворачиваем вектор грани, а не вектор челнока для удобства рассчёта, матрица поворота ([0,1],[-1,0])
    
    if railType == SGT.EWidthType.Narrow:
        r_vec = edge_vec
    elif railType == SGT.EWidthType.Wide:
        r_vec = edge_vec.rotate( -math.pi/2 )
    
    AgentEdgeAngle = agent_vec.angle( r_vec )

    if AgentEdgeAngle <= math.pi/4 :
        return math.degrees( r_vec.selfAngle() ), False
    elif AgentEdgeAngle >= math.pi * 3/4:
        return math.degrees( r_vec.rotate( math.pi ).selfAngle() ), True
    else:
        return agent_angle, None

def getAgentSide(nxGraph, tEdgeKey, agent_angle):
    railType = nxGraph.edges()[ tEdgeKey ][ SGA.widthType ]
    agent_vec = Vector2.fromAngle( math.radians( agent_angle ) )

    # Определяем вектор "право"
    # Для узкого рельса - это вектор, указывающий вправо от вектора челнока.
    # Так как направление "вперёд" для челнока на широком рельсе это вектор челнока, повернутый на +90 градусов,
    # то вектор "право" совпадает с вектором челнока
    if railType == SGT.EWidthType.Narrow:
        r_vec = agent_vec.rotate( -math.pi/2 )
    elif railType == SGT.EWidthType.Wide:
        r_vec = agent_vec

    deg_angle = math.degrees( r_vec.selfAngle() )

    return SGT.ESide.fromAngle( deg_angle )

def getFinalAgentAngle(nxGraph, agent_angle, agent_edge, nodes_route):
    for i in range( len(nodes_route) - 1  ):
        agent_edge = (nodes_route[i], nodes_route[i+1])
        agent_angle, direction = getAgentAngle( nxGraph = nxGraph, tEdgeKey = agent_edge, agent_angle = agent_angle )
    return agent_angle, agent_edge

def EdgeDisplayName( nodeID_1, nodeID_2 ): return nodeID_1 +" --> "+ nodeID_2

GraphML_ext_filters = {
                           "GraphML (*.graphml)" : "graphml",
                           "All Files (*)"       : ""
                       }

sGraphML_file_filters = ";;".join( GraphML_ext_filters.keys() )

def loadGraphML_File( sFName ):
    # загрузка графа и создание его объектов для сетевой синхронизации
    if not os.path.exists( sFName ):
        print( f"{SC.sWarning} GraphML file not found '{sFName}'!" )
        return None

    nxGraph = nx.read_graphml( sFName )
    # не используем атрибуты для значений по умолчанию для вершин и граней, поэтому сносим их из свойств графа
    # как и следует из документации новые ноды не получают этот список атрибутов, это просто кеш
    # при создании графа через загрузку они появляются, при создании чистого графа ( nx.Graph() ) нет
    del nxGraph.graph["node_default"]
    del nxGraph.graph["edge_default"]

    return nxGraph

def vecsFromNodes( nxGraph, baseNodeID, NeighborsIDs):        
    x1, y1 = getNodeCoords( nxGraph, baseNodeID )
    vecList = []

    for ID in NeighborsIDs:
        x2, y2 = getNodeCoords( nxGraph, ID )
        vec = Vector2 ( x2 - x1, - (y2 - y1) ).unit() #для координаты "y" берем отрицательное значение, тк в сцене ось "y" направлена вниз
        vecList.append(vec)

    return vecList

def vecsPair_withMaxAngle(vecs):
    vecs_Pairs = []
    c = len( vecs )

    if c < 2: return None

    for i in range( c ):
        for j in range (i+1, c):
            vecs_Pairs.append( (vecs[i], vecs[j]) )

    dictByAngle = {}
    for vec1, vec2 in vecs_Pairs:
        angle = vec1.angle( vec2 )
        dictByAngle[angle] = ( vec1, vec2 )
            
    return dictByAngle[ max(dictByAngle.keys()) ]

def rotateToRightSector(vec):
    angle = vec.selfAngle()
    if angle > math.pi/4 and angle <= math.pi * (5/4):
        vec = vec.rotate( math.pi )

    return vec

def rotateToLeftSector(vec):
    angle = vec.selfAngle()
    if angle <= math.pi/4 or angle > math.pi * (5/4):
        vec = vec.rotate( math.pi )

    return vec

def calcNodeMiddleLine ( nxGraph, nodeID, NeighborsIDs ):
    nodeVecs = vecsFromNodes( nxGraph = nxGraph, baseNodeID = nodeID, NeighborsIDs = NeighborsIDs )
    vecs_count = len(nodeVecs)

    r_vec = Vector2(1, 0)
    
    if vecs_count > 1:
        vec1, vec2 = vecsPair_withMaxAngle( nodeVecs )
        r_vec = vec1 + vec2

        #если вектора противоположнонаправлены, r_vec будет нулевым вектором,
        # тогда результирующий вектор берём как перпендикуляр vec1 или vec2 (выбираем вектор с меньшим углом)
        if  not r_vec:
            r_vec = vec1.rotate( math.pi/2 ) if ( vec1.selfAngle() < vec2.selfAngle() ) else vec2.rotate( math.pi/2 )

    elif vecs_count == 1:
        r_vec = nodeVecs[0].rotate( math.pi/2 )
    
    eNodeType = nxGraph.nodes[ nodeID ][ SGA.nodeType ]
    
    if eNodeType == SGT.ENodeTypes.StoragePoint:
        r_vec = rotateToRightSector( r_vec )
    elif eNodeType == SGT.ENodeTypes.PowerStation:
        eSide = nxGraph.nodes[ nodeID ][ SGA.chargeSide ]
        r_vec = rotateToLeftSector( r_vec ) if eSide == SGT.ESide.Left else rotateToRightSector( r_vec )
    
    return r_vec

def pathsIntersections( path_1, path_2 ):
    intersections = []
    i_path = []
    for nodeID in path_1:
        if nodeID in path_2:
            i_path.append( nodeID )
        elif len(i_path) > 0:
            intersections.append( i_path )
            i_path = []

    if len(i_path): intersections.append( i_path )
    return intersections

def closestCycleNode( nxGraph, nodeID, cycle ): #поиск ближайшей ноды в цикле cycle для ноды nodeID
    if nodeID in cycle: return nodeID
    
    path = nx.dijkstra_path( nxGraph, nodeID, cycle[0] )
    i = pathsIntersections( path, cycle )
    
    return i[0][0]

def remapCycle( targetStartNodeID, cycle ): # remapCycle(targetStartNodeID = '3', cycle = [ '1', '2', '3', '4' ]) == [ '3', '4', '1', '2' ]
    start_idx = cycle.index( targetStartNodeID )
    cycle = cycle[start_idx:] + cycle[:start_idx]
    return cycle

def mergeCycleWithPath( cycle, simple_path ):
    assert len(simple_path) == len( set(simple_path) ), f"{SC.sAssert} {simple_path} not a simple path (contains dublicates)."

    i = pathsIntersections( simple_path, cycle )

    # не расматриваем вариант, если нет пересечений
    # не рассматриваем варианты если цикл пересекается с путём несколько раз (значит есть более короткие циклы)
    if len( i ) != 1: return None
    
    enterNode = i[0][0]
    outNode   = i[0][-1]
    cycle = remapCycle(enterNode, cycle )

    path_e_idx = simple_path.index( enterNode )
    path_o_idx = simple_path.index( outNode )

    cy_o_idx = cycle.index( outNode )
    
    # пример
    # simple_path = [ 0,1,2,3,4,5 ]  cycle =  [1,2,3,71,70]  merged = [0, 1, 2, 3, 71, 70, 1, 2, 3, 4, 5]
    # simple_path = [ 0,1,2,3,4,5 ]  cycle =  [1,70,71,3,2]  merged = [0, 1, 70, 71, 3, 4, 5]
    
    if (cycle[1] in simple_path) or (enterNode == outNode): # направление цикла совпадает с направлением пути или пересечение - одна нода
        merged = simple_path[:path_o_idx] + cycle[cy_o_idx:] + simple_path[path_e_idx:]
    else:
        merged = simple_path[:path_e_idx] + cycle[:cy_o_idx] + simple_path[path_o_idx:]

    return merged

def pathWithTargetCycle(nxGraph, startNodeID, targetNodeID, cycle):
    enterNode = closestCycleNode( nxGraph, startNodeID, cycle )

    pathToCycle   = nx.dijkstra_path( nxGraph, startNodeID, enterNode )
    pathFromCycle = nx.dijkstra_path( nxGraph, enterNode, targetNodeID )
    cycle = remapCycle( enterNode, cycle )

    finalPath = pathToCycle + cycle[1:] + pathFromCycle

    return finalPath

def pathsThroughCycles( nxGraph, simple_path ):
    it_cycles = nx.simple_cycles( nxGraph )
    cycles = [ c for c in it_cycles if len(c) > 3 ] #циклы с кратными гранями (a->b->a) отбрасываем

    paths_through_cycles = []

    for c in cycles:
        path = mergeCycleWithPath( c, simple_path )
        
        if path is None:
            startNodeID, targetNodeID = simple_path[0], simple_path[-1]
            path = pathWithTargetCycle( nxGraph, startNodeID, targetNodeID, c )

        paths_through_cycles.append( path )

    return paths_through_cycles

def pathWeight( nxGraph, path, weight = SGA.edgeSize):
    if weight is None:
        return( len(path) - 1 )
    
    edges = edgesListFromNodes( path )
    path_weight = 0
    
    for tEdgeKey in edges:
        path_weight += nxGraph.edges()[ tEdgeKey ].get( weight )

    return path_weight

def findNodes( nxGraph, prop, value ):
    return [ node[0] for node in nxGraph.nodes( data = prop ) if node[1] == value ]

def makeNodesRoutes( nxGraph, agentEdge, agentAngle, targetNode, targetSide = None ):
    dijkstra_path = nx.algorithms.dijkstra_path( nxGraph, agentEdge[0], targetNode)

    if targetSide is None:
        return [dijkstra_path]

    final_agentAngle, final_agentEdge = getFinalAgentAngle( nxGraph = nxGraph, agent_angle = agentAngle,
                                                            agent_edge = agentEdge, nodes_route = dijkstra_path )
    eAgentSide = getAgentSide( nxGraph, final_agentEdge, final_agentAngle )

    if targetSide == eAgentSide:
        return [dijkstra_path]

    paths_through_cycles = pathsThroughCycles( nxGraph, dijkstra_path )
    paths_correct_side = []

    for path in paths_through_cycles:
        final_agentAngle, final_agentEdge = getFinalAgentAngle( nxGraph = nxGraph, agent_angle = agentAngle,
                                                                agent_edge = agentEdge, nodes_route = path )
        eAgentSide = getAgentSide( nxGraph, final_agentEdge, final_agentAngle )

        if targetSide == eAgentSide:
            paths_correct_side.append( path )

    return paths_correct_side

def shortestNodesRoute( nxGraph, agentEdge, agentAngle, targetNode, targetSide = None ):
    nodes_routes = makeNodesRoutes( nxGraph, agentEdge, agentAngle, targetNode, targetSide = targetSide )
    nodes_routes_weighted = [ (pathWeight(nxGraph, route), route) for route in nodes_routes ]
    
    if len( nodes_routes_weighted ) > 0:
        return min( nodes_routes_weighted, key = lambda weighted_route: weighted_route[0] )
    
    return 0, []

def routeToServiceStation( nxGraph, agentEdge, agentAngle ):
    charge_nodes = findNodes( nxGraph, SGA.nodeType, SGT.ENodeTypes.PowerStation )
    nodes_routes_weighted = []

    for targetNode in charge_nodes:
        targetSide = nxGraph.nodes()[ targetNode ][ SGA.chargeSide ]
        weighted_route = shortestNodesRoute( nxGraph, agentEdge, agentAngle, targetNode, targetSide = targetSide )

        nodes_routes_weighted.append( weighted_route )
    
    if len( nodes_routes_weighted ) > 0:
        return min( nodes_routes_weighted, key = lambda weighted_route: weighted_route[0] )

    return 0, []