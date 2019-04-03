
import math
import networkx as nx
import numpy as np
import os
import re

# рассчет угла поворота линии (в единичной окружности, т.е. положительный угол - против часовой стрелки, ось х - 0 градусов)

def tEdgeKeyFromStr( edge_str ):
    pattern = " |,|:|-"
    return re.split(pattern, edge_str)

def tEdgeKeyToStr( tEdgeKey, bReversed = False ):
    if bReversed:
        tEdgeKey = tuple( reversed(tEdgeKey) )
    return f"{tEdgeKey[0]} {tEdgeKey[1]}"

def getLineAngle( line ):
    rAngle = math.acos( line.dx() / ( line.length() or 1) )
    if line.dy() >= 0: rAngle = (math.pi * 2.0) - rAngle
    return rAngle

def getUnitVector( x, y ):
    h: float =  np.hypot(x, y)
    try:
        return np.array( [ x/h, y/h ], float )
    except ZeroDivisionError:
        return np.array( [ 0, 0 ], float )

def getUnitVector_RadAngle( x, y ):
    rAngle = np.arccos( x ) if y >= 0 else 2*np.pi - np.arccos( x )
    return rAngle

def getUnitVector_DegAngle( x, y ):
    return float( np.degrees( getUnitVector_RadAngle(x, y) ) )

def getUnitVector_FromDegAngle( angle ):
    angle = np.radians( angle % 360 )
    x = np.cos(angle)
    y = np.sin(angle) if angle <= 180 else - np.sin(angle)
    return np.array( [x, y], float )

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
