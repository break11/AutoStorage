
import networkx as nx
from Net.NetObj import *
from .StorageGrafTypes import *

class CGrafRoot_NO( CNetObj ):
    __s_ncGraf = "nxGraf"
    def __init__( self, name="", parent=None, id=None, **kwargs ):
        if kwargs.get( self.__s_ncGraf ):
            self.nxGraf = kwargs[ self.__s_ncGraf ]
        super().__init__( name=name, parent=parent, id=id )

    def propsDict(self): return self.nxGraf.graph
    def onLoadFromRedis( self, netLink, netObj ):
        super().onLoadFromRedis( netLink, netObj )
        self.nxGraf = nx.DiGraph()

        d = netLink.hgetall( f"{self.redisBase_Name()}:props" )
        d1 = {}
        for k,v in d.items():
            k1 = k.decode() 
            v1 = v.decode()
            d1[ k1 ] = adjustAttrType( k1, v1 )

        self.nxGraf.graph = d1

    def onSendToRedis( self, netLink ):
        super().onSendToRedis( netLink )
        if len( self.propsDict() ):
            netLink.hmset( f"{self.redisBase_Name()}:props", self.propsDict() )

###################################################################################

class CGrafNode_NO( CNetObj ):
    def propsDict(self): return self.nxNode()

    def nxGraf(self): return self.grafNode().nxGraf
    def nxNode(self): return self.nxGraf().nodes()[ self.name ]
    def grafNode(self): return self.resolvePath('../../')

###################################################################################

class CGrafEdge_NO( CNetObj ):
    def __init__( self, name="", parent=None, nxEdge=None, id=None ):
        super().__init__( name = name, parent = parent, id=id )
        self.nxEdge = nxEdge

    def propsDict(self): return self.nxEdge
