

# class TreeObj:
#     def props(): return Dict()
#     def propCount(): return 0
#     def owner(): return 0

# from anytree import AnyNode, RenderTree


# root = AnyNode(id="root")
# s0 = AnyNode(id="sub0", parent=root)
# s0b = AnyNode(id="sub0B", parent=s0, foo=4, bar=109)
# s0a = AnyNode(id="sub0A", parent=s0)
# s1 = AnyNode(id="sub1", parent=root)
# s1a = AnyNode(id="sub1A", parent=s1)
# s1b = AnyNode(id="sub1B", parent=s1, bar=8)
# s1c = AnyNode(id="sub1C", parent=s1)
# s1ca = AnyNode(id="sub1Ca", parent=s1c)

# print( RenderTree(root) )


import networkx as nx

from anytree.resolver import Resolver
from anytree.importer import DictImporter
from anytree import RenderTree
from anytree import AnyNode, NodeMixin, RenderTree

from enum import *

nUID_Gen = 0

def genUID():
    global nUID_Gen
    nUID_Gen += 1
    return nUID_Gen

class ENodeTypes( Enum ):
    std    = auto()
    Graf   = auto()
    GNode  = auto()
    GEdge  = auto()

class CNetNode( NodeMixin ):
    def __init__( self, name="", parent=None, type_=ENodeTypes.std ):
        super().__init__()
        self.UID    = genUID()
        self.name   = name
        self.parent = parent
        self.type_  = type_

    def __repr__(self): return f'{str(self.UID)} {self.name} { (lambda: "" if self.type_ == ENodeTypes.std else "[" + self.type_.name + "]")() }'

class CGrafNode( CNetNode ):
    def __init__( self, name="", parent=None):
        super().__init__( name = name, parent = parent, type_= ENodeTypes.Graf )
        self.nxGraf = None

class CNodeNode( CNetNode ):
    def __init__( self, name="", parent=None):
        super().__init__( name = name, parent = parent, type_= ENodeTypes.GNode )

    def nxGraf(self):
        return self.grafNode().nxGraf

    def grafNode(self):
        r = Resolver('name')
        return r.get(self, '../../')

class CEdgeNode( CNetNode ):
    def __init__( self, name="", parent=None):
        super().__init__( name = name, parent = parent, type_= ENodeTypes.GEdge )

importer = DictImporter()

nxGraf  = nx.read_graphml( "GraphML/test.graphml" )
# nxGraf  = nx.read_graphml( "GraphML/magadanskaya_vrn.graphml" )

root2 = AnyNode(id="0", name="root2")

root  = CNetNode(name="root")
Graf  = CGrafNode(name="Graf", parent=root)
Nodes = CNetNode(name="Nodes", parent=Graf)
Edges = CNetNode(name="Edges", parent=Graf)

for nodeID in nxGraf.nodes():
    node = CNodeNode(name=nodeID, parent=Nodes)
    for k,v in nxGraf.nodes().items():
        prop = CNetNode( name=k,  )

for edgeID in nxGraf.edges():
     edge = CEdgeNode(name=edgeID, parent=Edges)

print( RenderTree(root) )
