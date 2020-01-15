import sys
import os
import networkx as nx

from Lib.Common.StrConsts import SC
from Lib.Common.Utils import mergeDicts
import Lib.GraphEntity.StorageGraphTypes as SGT
from Lib.GraphEntity.Graph_NetObjects import CGraphNode_NO, CGraphEdge_NO, common_NodeProps, spec_NodeProps

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

def convertTo_TransporterVersion( nxGraph ):
    print( "********************** convertTo_TransporterVersion ***************************" )

    # переименование типов нод
    fieldsToRename = { "DummyNode"      : "RailNode",
                       "UnknownType"    : "DummyNode",
                       "StorageSingle"  : "Storage",
                       "PickStationIn"  : "PickStation",
                       "PickStationOut" : "PickStation",
                       "ServiceStation" : "PowerStation",
                       "Cross"          : "RailCross"
    }
    renameNodeTypes( nxGraph, fieldsToRename )

    SGT.prepareGraphProps( nxGraph )

    # добавление недостающих свойств для нод
    for k,v in nxGraph.nodes().items():
        propList = common_NodeProps
        nodeType = v[ SGT.SGA.nodeType ]
        if nodeType in spec_NodeProps:
            propList = propList.union( spec_NodeProps[ nodeType ] )
        
        for propName in propList:
            if propName not in v:
                v[ propName ] = CGraphNode_NO.def_props[ propName ]

    SGT.prepareGraphProps( nxGraph, bToEnum=False )

###############################################################################################
        
def converToPython( nxGraph ):
    convertFromHaskell( nxGraph )
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

    SGT.prepareGraphProps( nxGraph, bToEnum = False )
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
