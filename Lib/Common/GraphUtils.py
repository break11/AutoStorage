
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
        return agent_angle, None


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
