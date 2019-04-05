
import math
import networkx as nx
import os
import re

from Lib.Common import StorageGraphTypes as SGT

# рассчет угла поворота линии (в единичной окружности, т.е. положительный угол - против часовой стрелки, ось х - 0 градусов)

def tEdgeKeyFromStr( edge_str ):
    pattern = " |,|:|-"
    return tuple (re.split(pattern, edge_str))

def tEdgeKeyToStr( tEdgeKey, bReversed = False ):
    k = tEdgeKey
    if bReversed:
        tEdgeKey = tuple( reversed(tEdgeKey) )
    
    return f"{tEdgeKey[0]} {tEdgeKey[1]}"

def getLineAngle( line ):
    rAngle = math.acos( line.dx() / ( line.length() or 1) )
    if line.dy() >= 0: rAngle = (math.pi * 2.0) - rAngle
    return rAngle

def getUnitVector( x, y ):
    h: float =  math.hypot(x, y)
    try:
        return ( x/h, y/h )
    except ZeroDivisionError:
        return (0, 0)

def getUnitVector_RadAngle( x, y ):
    rAngle = math.acos( x ) if y >= 0 else 2*math.pi - math.acos( x )
    return rAngle

def getUnitVector_DegAngle( x, y ):
    return float( math.degrees( getUnitVector_RadAngle(x, y) ) )

def getUnitVector_FromDegAngle( angle ):
    angle = math.radians( angle % 360 )
    x = math.cos(angle)
    y = math.sin(angle) if angle <= 180 else - math.sin(angle)
    return (x, y)

def getEdgeCoords (nxGraph, tEdgeKey):
    nodeID_1, nodeID_2 = tEdgeKey[0], tEdgeKey[1]

    if not nxGraph.has_edge( nodeID_1, nodeID_2 ):
        return

    x1 = nxGraph.nodes()[ nodeID_1 ][SGT.s_x]
    y1 = nxGraph.nodes()[ nodeID_1 ][SGT.s_y]
    
    x2 = nxGraph.nodes()[ nodeID_2 ][SGT.s_x]
    y2 = nxGraph.nodes()[ nodeID_2 ][SGT.s_y]

    return x1, x2, y1, y2

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
