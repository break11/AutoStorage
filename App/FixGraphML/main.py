import sys
import os
import networkx as nx

from Lib.Common import StrConsts as SC

graphAttr = {
                "widthType"        : str,
                "edgeSize"         : int,
                "highRailSizeFrom" : int,
                "highRailSizeTo"   : int,
                "curvature"        : str,
                "edgeType"         : str,
                "sensorSide"       : str,
                "chargeSide"       : str,
                "containsAgent"    : int,
                "floor_num"        : int,
                "x"                : int,
                "y"                : int,
                "nodeType"         : str,
                "storageType"      : str,
             }

def adjustAttr( sAttrName, val ):
    if val is None: return None

    # для атрибутов, которых нет в списке возвращаем без преобразования типа
    if not graphAttr.get( sAttrName ):
        return val
    
    val = ( graphAttr[ sAttrName ] )( val )
    return val

def adjustGraphPropsDict( d ):
    d1 = {}
    for k,v in d.items():
        d1[ k ] = adjustAttr( k, v )
    return d1


attr_to_del = [
                "node_default", "edge_default", "name",
                "containsAgent", "floor_num", "edgeType",
              ]

def load_and_fix_GraphML_File( sFName ):
    # загрузка графа и создание его объектов для сетевой синхронизации
    if not os.path.exists( sFName ):
        print( f"{SC.sWarning} GraphML file not found '{sFName}'!" )
        return None

    print( f"Fixing {sFName} ..." )

    nxGraph = nx.read_graphml( sFName )

    nxGraph.graph = adjustGraphPropsDict( nxGraph.graph )
    print( "Adjust graph props types." )
    
    for attrName in attr_to_del:
        if nxGraph.graph.get( attrName ) is not None:
            print( f"Del attr {attrName} from graph props." )
            del nxGraph.graph[ attrName ]

    #***********************************

    print( f"Adjust nodes props types." )
    for k,v in nxGraph.nodes().items():
        d = adjustGraphPropsDict( v )
        nxGraph.nodes()[ k ].update( d )

        for attrName in attr_to_del:
            if nxGraph.nodes()[k].get( attrName ) is not None:
                print( f"Del attr {attrName} from node '{k}' props." )
                del nxGraph.nodes()[k][ attrName ]

    #***********************************

    print( f"Adjust edges props types." )
    for k,v in nxGraph.edges().items():
        d = adjustGraphPropsDict( v )
        nxGraph.edges()[ k ].update( d )

        for attrName in attr_to_del:
            if nxGraph.edges()[k].get( attrName ) is not None:
                print( f"Del attr {attrName} from edge '{k}' props." )
                del nxGraph.edges()[k][ attrName ]

    nx.write_graphml( nxGraph, sFName )

def main():
    if len(sys.argv) < 2:
        print( "Usage: FixGraphML 'filename.graphml' --> for fix one file" )
        print( "Usage: FixGraphML --all              --> for fix all graphml in ./GraphML dir" )
        return 1

    if sys.argv[1] == "--all":
        for root, dirs, files in os.walk("./GraphML"):
            for file in files:
                if file.endswith(".graphml"):
                    sFName = os.path.join(root, file)
                    load_and_fix_GraphML_File( sFName )
    else:
        load_and_fix_GraphML_File( sys.argv[1] )

    return 0
