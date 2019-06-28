
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