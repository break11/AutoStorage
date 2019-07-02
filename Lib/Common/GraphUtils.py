
import math
import networkx as nx
import os
import re

from Lib.Common import StorageGraphTypes as SGT
from Lib.Common.Vectors import Vector2
import Lib.Common.StrConsts as SC

# рассчет угла поворота линии (в единичной окружности, т.е. положительный угол - против часовой стрелки, ось х - 0 градусов)

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
    return nxGraph.edges()[ tKey ][ SGT.s_edgeSize ]

def nodeType(nxGraph, nodeID):
    return nxGraph.nodes()[ nodeID ][ SGT.s_nodeType ]

def tEdgeKeyFromStr( edge_str ):
    return tuple( nodesList_FromStr( edge_str) )

def tEdgeKeyToStr( tEdgeKey, bReversed = False ):    
    return f"{tEdgeKey[0]} {tEdgeKey[1]}"

def getEdgeCoords (nxGraph, tEdgeKey):
    nodeID_1, nodeID_2 = tEdgeKey[0], tEdgeKey[1]

    if not nxGraph.has_edge( nodeID_1, nodeID_2 ):
        return

    x1 = nxGraph.nodes()[ nodeID_1 ][SGT.s_x]
    y1 = nxGraph.nodes()[ nodeID_1 ][SGT.s_y]
    
    x2 = nxGraph.nodes()[ nodeID_2 ][SGT.s_x]
    y2 = nxGraph.nodes()[ nodeID_2 ][SGT.s_y]

    return x1, y1, x2, y2

def getNodeCoords (nxGraph, nodeID):

    if not nxGraph.has_node( nodeID ):
        return

    x = nxGraph.nodes()[ nodeID ][SGT.s_x]
    y = nxGraph.nodes()[ nodeID ][SGT.s_y]
    
    return x, y

def getAgentAngle(nxGraph, tEdgeKey, agent_angle):

    edgeCoords = getEdgeCoords( nxGraph, tEdgeKey )
    if edgeCoords is None: return agent_angle, False

    x1, y1, x2, y2 = edgeCoords

    edge_vec = Vector2( x2 - x1, - (y2 - y1) ) #берём отрицательное значение "y" тк, значения по оси "y" увеличиваются по направлению вниз
    
    s_EdgeType = nxGraph.edges()[ tEdgeKey ].get( SGT.s_widthType )
    railType = SGT.EWidthType.fromString( s_EdgeType )
    
    agent_vec = Vector2.fromAngle( math.radians( agent_angle ) )
    
    #Если рельс широкий, используем для рассчёта повернутый на -90 градусов вектор грани,
    #так как направление "вперёд" для челнока на широком рельсе это вектор челнока, повернутый на +90 градусов
    #поворачиваем вектор грани, а не вектор челнока для удобства рассчёта, матрица поворота ([0,1],[-1,0])
    
    if railType == SGT.EWidthType.Narrow:
        r_vec = edge_vec
    elif railType == SGT.EWidthType.Wide:
        r_vec = edge_vec.rotate( -math.pi/2 )
    
    AgentEdgeAngle = agent_vec.angle( r_vec )

    if AgentEdgeAngle < math.pi/4 :
        return r_vec.selfAngle(), False
    elif AgentEdgeAngle > math.pi * 3/4:
        return r_vec.rotate( math.pi ).selfAngle(), True
    else:
        return agent_angle, None # ??? переводить agent_angle в радианы для однообразия

def getFinalAgentAngle(nxGraph, agent_angle, nodes_route):
    for i in range( len(nodes_route) - 1  ):
        tKey = (nodes_route[i], nodes_route[i+1])
        agent_angle, direction = getAgentAngle( nxGraph, tKey, agent_angle )
        agent_angle = math.degrees( agent_angle )
    return agent_angle

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
        
    Neighbors_count = len(NeighborsIDs)
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
    if angle > math.pi/4 and angle < math.pi * (5/4):
        vec = vec.rotate( math.pi )

    return vec

def rotateToLeftSector(vec):
    angle = vec.selfAngle()
    if angle < math.pi/4 or angle > math.pi * (5/4):
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
    
    eNodeType = SGT.ENodeTypes.fromString( nxGraph.nodes[ nodeID ][ SGT.s_nodeType ] )
    
    if eNodeType == SGT.ENodeTypes.StorageSingle:
        r_vec = rotateToRightSector( r_vec )
    elif eNodeType == SGT.ENodeTypes.ServiceStation:
        eSide = SGT.ESide.fromString( nxGraph.nodes[ nodeID ][ SGT.s_chargeSide ] )
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

def closestCycleNode( nxGraph, nodeID, cycle ):
    if nodeID in cycle: return nodeID
    
    path = nx.dijkstra_path( nxGraph, nodeID, cycle[0] )

    i = pathsIntersections( path, cycle )
    
    if len(i): return i[0][0]

def remapCycle( targetStartNodeID, cycle ):
    start_idx = cycle.index( targetStartNodeID )
    cycle = cycle[start_idx:] + cycle[:start_idx]
    return cycle

def mergeCycleWithPath( cycle, simple_path ):
    s_cycle = set(cycle)
    s_simple_path = set(simple_path)

    assert len(simple_path) == len(s_simple_path), f"{SC.sAssert} {simple_path} not a simple path (contains dublicates)."

    if len( s_cycle.intersection( s_simple_path ) ) == 0: return None

    # simple_path = [ 0,1,2,3,4,5 ]  cycle =  [1,2,3,71,70]  merged = [0, 1, 2, 3, 71, 70, 1, 2, 3, 4, 5]
    # simple_path = [ 0,1,2,3,4,5 ]  cycle =  [1,70,71,3,2]  merged = [0, 1, 70, 71, 3, 4, 5]
    
    i = pathsIntersections( simple_path, cycle )
    if len(i) > 1: return None #не рассматриваем варианты если цикл пересекается с путём несколько раз, значит есть более короткие циклы

    enterNode = i[0][0]
    outNode   = i[0][-1]
    cycle = remapCycle(enterNode, cycle )

    path_e_idx = simple_path.index(enterNode)
    path_o_idx = simple_path.index( outNode )

    cy_e_idx = cycle.index(enterNode)
    cy_o_idx = cycle.index( outNode )
    
    if cycle[1] in simple_path: # направление цикла совпадает с направлением пути
        merged = simple_path[:path_o_idx] + cycle[cy_o_idx:] + simple_path[path_e_idx:]
    else:
        merged = simple_path[:path_e_idx] + cycle[:cy_o_idx] + simple_path[path_o_idx:]

    return merged