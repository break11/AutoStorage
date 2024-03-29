import sys
import os
import networkx as nx

from Lib.Common.StrConsts import SC
from Lib.Common.Utils import mergeDicts
import Lib.GraphEntity.StorageGraphTypes as SGT
import Lib.GraphEntity.Graph_NetObjects as GNO

def adjustAttr( sAttrName, val, graphAttr ):
    if val is None: return None

    # для атрибутов, которых нет в списке возвращаем без преобразования типа
    if not graphAttr.get( sAttrName ):
        return val
    
    val = ( graphAttr[ sAttrName ] )( val )
    return val

def adjustGraphPropsDict( d, graphAttr ):
    d1 = {}
    for k,v in d.items():
        d1[ k ] = adjustAttr( k, v, graphAttr )
    return d1

###############################################################################################

def convertFromHaskell( nxGraph ):
    print( "********************** convertFromHaskell ***************************" )
    graphAttr = {
                "nodeType"         : str,
                "edgeType"         : str,
                "widthType"        : str,
                "edgeSize"         : int,
                "highRailSizeFrom" : int,
                "highRailSizeTo"   : int,
                "curvature"        : str,
                "sensorSide"       : str,
                "chargeSide"       : str,
                "x"                : int,
                "y"                : int,

                "floor_num"        : int,
                "containsAgent"    : int,
             }

    attr_to_del = [
                    "node_default", "edge_default", "name",
                    "containsAgent", "floor_num", "edgeType",
                ]

    print( "Convert to Python format." )

    nxGraph.graph = adjustGraphPropsDict( nxGraph.graph, graphAttr )
    print( "Adjust graph props types." )
    
    for attrName in attr_to_del:
        if nxGraph.graph.get( attrName ) is not None:
            print( f"Del attr {attrName} from graph props." )
            del nxGraph.graph[ attrName ]

    #***********************************

    print( f"Adjust nodes props types and adding needed props." )
    for k,v in nxGraph.nodes().items():
        d = adjustGraphPropsDict( v, graphAttr )
        nxGraph.nodes()[ k ].update( d )

        for attrName in attr_to_del:
            if nxGraph.nodes()[k].get( attrName ) is not None:
                print( f"Del attr {attrName} from node '{k}' props." )
                del nxGraph.nodes()[k][ attrName ]

    #***********************************

    print( f"Adjust edges props types and adding needed props." )
    for k,v in nxGraph.edges().items():
        d = adjustGraphPropsDict( v, graphAttr )
        nxGraph.edges()[ k ].update( d )

        for attrName in attr_to_del:
            if nxGraph.edges()[k].get( attrName ) is not None:
                print( f"Del attr {attrName} from edge '{k}' props." )
                del nxGraph.edges()[k][ attrName ]

###############################################################################################

def renameNodeTypes( nxGraph, renameDict ):
    for oldNodeTypeName, newNodeTypeName in renameDict.items():
        for nodeName,nodeProps in nxGraph.nodes().items():
            if nodeProps[ SGT.SGA.nodeType ] == oldNodeTypeName:
                nodeProps[ SGT.SGA.nodeType ] = newNodeTypeName

def renameProps( itemsDict, renameDict ):
    for itemName in itemsDict.keys():
        for old, new in renameDict.items():
            if old in itemsDict[ itemName ]:
                itemsDict[ itemName ][new] = itemsDict[ itemName ][old]
                del itemsDict[ itemName ][old]

def convertTo_TransporterVersion( nxGraph ):
    print( "********************** convertTo_TransporterVersion ***************************" )

    # переименование типов нод
    d = { "DummyNode"      : "RailPoint",
          "UnknownType"    : "DummyNode",
          "StorageSingle"  : "StoragePoint",
          "PickStationIn"  : "PickStation",
          "PickStationOut" : "PickStation",
          "ServiceStation" : "PowerStation",
          "Cross"          : "RailCross"
    }
    renameNodeTypes( nxGraph, d )

    d = { "chargePort" : "chargeAddress" }
    renameProps( nxGraph.nodes(), d )

    SGT.prepareGraphProps( nxGraph )
    
    # добавление недостающих свойств для Граней и Нод
    def normalizeObjectsProps( objDict, typePropName, commonProps, specProps, defPropsVal ):
        for k,v in objDict.items():
            # поле Type отсутствовало в дикте свойств, добавляем его туда с дефолтным значением
            if typePropName not in v:
                v[ typePropName ] = defPropsVal[ typePropName ]

            propList = commonProps
            objType = v[ typePropName ]
            if objType in specProps:
                propList = propList.union( { propName for propName, val in specProps[ objType ].items() if val } )

            for propName in propList:
                if propName not in v:
                    v[ propName ] = defPropsVal[ propName ]

    normalizeObjectsProps( nxGraph.nodes(), SGT.SGA.nodeType, GNO.common_NodeProps, GNO.spec_NodeProps, GNO.CGraphNode_NO.def_props )
    normalizeObjectsProps( nxGraph.edges(), SGT.SGA.edgeType, GNO.common_EdgeProps, GNO.spec_EdgeProps, GNO.CGraphEdge_NO.def_props )

    SGT.prepareGraphProps( nxGraph, bToEnum=False )

###############################################################################################
        
def converToPython( nxGraph ):
    # convertFromHaskell( nxGraph )
    convertTo_TransporterVersion( nxGraph )

###############################################################################################

def load_and_fix_GraphML_File( sFName="" ):
    # загрузка графа и создание его объектов для сетевой синхронизации
    if not os.path.exists( sFName ):
        print( f"{SC.sWarning} GraphML file not found '{sFName}'!" )
        return None

    print( f"Fixing {sFName} ..." )

    nxGraph = nx.read_graphml( sFName )

    converToPython( nxGraph )

    nx.write_graphml( nxGraph, sFName )

def main():
    if len(sys.argv) < 2:
        print( "Usage: FixGraphML 'filename.graphml' --> for fix one file" )
        print( "Usage: FixGraphML --all              --> for fix all graphml in ./GraphML dir" )
        return 1

    if sys.argv.count( "--all" ) >0:
        for root, dirs, files in os.walk("./GraphML"):
            for file in files:
                if file.endswith(".graphml"):
                    sFName = os.path.join(root, file)
                    load_and_fix_GraphML_File( sFName=sFName )
    else:
        load_and_fix_GraphML_File( sFName=sys.argv[1] )

    return 0
