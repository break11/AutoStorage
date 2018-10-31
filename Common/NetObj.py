
from anytree import NodeMixin

from enum import *

nUID_Gen = 0

def genUID():
    global nUID_Gen
    nUID_Gen += 1
    return nUID_Gen

class ENetObjTypes( Enum ):
    std    = auto()
    Graf   = auto()
    GNode  = auto()
    GEdge  = auto()

class CNetObj( NodeMixin ):
    def __init__( self, name="", parent=None, type_=ENetObjTypes.std ):
        super().__init__()
        self.UID    = genUID()
        self.name   = name
        self.parent = parent
        self.type_  = type_

    def afterLoad( self ):
        pass

    def afterUpdate( self ):
        pass

    def __repr__(self): return f'{str(self.UID)} {self.name} { (lambda: "" if self.type_ == ENetObjTypes.std else "[" + self.type_.name + "]")() }'

class CGraf_NO( CNetObj ):
    def __init__( self, name="", parent=None):
        super().__init__( name = name, parent = parent, type_= ENetObjTypes.Graf )
        self.nxGraf = None

    def afterLoad( self ):
        # create nxGraf from childNodes
        pass

class CNode_NO( CNetObj ):
    def __init__( self, name="", parent=None):
        super().__init__( name = name, parent = parent, type_= ENetObjTypes.GNode )

    def nxGraf(self):
        return self.grafNode().nxGraf

    def grafNode(self):
        r = Resolver('name')
        return r.get(self, '../../')

class CEdge_NO( CNetObj ):
    def __init__( self, name="", parent=None):
        super().__init__( name = name, parent = parent, type_= ENetObjTypes.GEdge )
