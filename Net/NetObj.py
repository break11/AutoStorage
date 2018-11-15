# from . import NetObj_Manager

import sys

from anytree import NodeMixin

from Common.SettingsManager import CSettingsManager as CSM

class CNetObj( NodeMixin ):
    __sName    = "Name"
    __sUID     = "UID"
    __sType    = "Type"
    __sTypeUID = "TypeUID"
    __modelHeaderData = [ __sName, __sUID, __sType, __sTypeUID, ]

    typeUID = 0 # fill after registration --> registerType

    def __init__( self, name="", parent=None ):
        super().__init__()
        self.UID     = CNetObj_Manager.genNetObj_UID()
        self.name    = name
        self.parent  = parent
        self.isUpdated = False

        hd = self.__modelHeaderData
        self.__modelData = {
                            hd.index( self.__sName    ) : self.name,
                            hd.index( self.__sUID     ) : self.UID,
                            hd.index( self.__sType    ) : self.__class__.__name__,
                            hd.index( self.__sTypeUID ) : self.typeUID,
                            }

        CNetObj_Manager.registerObj( self )

    def __del__(self):
        print("CNetObj destructor", self)
        CNetObj_Manager.unregisterObj( self )

###################################################################################

    def prepareDelete(self):
        for child in self.children:
            child.prepareDelete()
            child.parent = None
            child.children = []
        self.parent = None

    def clearChildren(self):
        for child in self.children:
            child.prepareDelete()

###################################################################################

    @classmethod
    def modelDataColCount( cls ): return len( cls.__modelHeaderData )
    @classmethod
    def modelHeaderData( cls, col ): return cls.__modelHeaderData[ col ]
    def modelData( self, col ): return self.__modelData[ col ]

    def propsDict(self): raise NotImplementedError

###################################################################################
    def sendToNet( self, netLink ):
        netLink.set( f"obj:{self.UID}:{self.name}", self.name )
        netLink.set( f"obj:{self.UID}:{self.__class__.typeUID}", self.__class__.typeUID )

    def afterLoad( self ):
        pass

    def afterUpdate( self ):
        pass

    def __repr__(self): return f'{str(self.UID)} {self.name} {str( self.typeUID )}'

###################################################################################

class CGrafRoot_NO( CNetObj ):
    def __init__( self, name="", parent=None, nxGraf=None):
        super().__init__( name = name, parent = parent )
        self.nxGraf = nxGraf

    def propsDict(self): return self.nxGraf.graph

    def afterLoad( self ):
        # create nxGraf from childNodes
        pass

class CGrafNode_NO( CNetObj ):
    def __init__( self, name="", parent=None, nxNode=None):
        super().__init__( name = name, parent = parent )
        self.nxNode = nxNode

    def propsDict(self): return self.nxNode

    # def nxGraf(self):
    #     return self.grafNode().nxGraf

    def grafNode(self):
        # r = Resolver('name')
        # return r.get(self, '../../')
        pass

    def afterLoad( self ):
        # graf = queryNode(self, '../../', CGrafRoot_NO)

        # for attr
        #     graf.nxGraf().nodes[ name ][ attr ] = val
        # # create nxGraf from childNodes
        pass

class CGrafEdge_NO( CNetObj ):
    def __init__( self, name="", parent=None, nxEdge=None):
        super().__init__( name = name, parent = parent )
        self.nxEdge = nxEdge

    def propsDict(self): return self.nxEdge

from .NetObj_Manager import CNetObj_Manager
