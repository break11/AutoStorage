
from anytree import NodeMixin

from typing import Dict

class CNetObj_TypeManager:
    __genTypeUID = 0
    __nodeTypes : Dict[ int, object ] = {}

    @classmethod
    def registerType(cls, netObjClass):
        assert issubclass( netObjClass, CNetObj ), "netObjClass must be instance of CNetObj!"
        cls.__genTypeUID += 1
        cls.__nodeTypes[ cls.__genTypeUID ] = netObjClass
        netObjClass.typeUID = cls.__genTypeUID
        return cls.__genTypeUID

    # @classmethod
    # def nodeTypeUID(cls, nodeType):
    #     return cls.__nodeTypes[ nodeType ]

genNodeObj_UID = 0

def genUID():
    global genNodeObj_UID
    genNodeObj_UID += 1
    return genNodeObj_UID

class CNetObj( NodeMixin ):
    __sName    = "Name"
    __sUID     = "UID"
    __sType    = "Type"
    __sTypeUID = "TypeUID"
    __modelHeaderData = [ __sName, __sUID, __sType, __sTypeUID, ]

    typeUID = 0 # fill after registration --> registerType

    def __init__( self, name="", parent=None ):
        super().__init__()
        self.UID     = genUID()
        self.name    = name
        self.parent  = parent

        hd = self.__modelHeaderData
        self.__modelData = {
                            hd.index( self.__sName    ) : self.name,
                            hd.index( self.__sUID     ) : self.UID,
                            hd.index( self.__sType    ) : self.__class__.__name__,
                            hd.index( self.__sTypeUID ) : self.typeUID,
                            }

    @classmethod
    def modelDataColCount( cls ): return len( cls.__modelHeaderData )
    @classmethod
    def modelHeaderData( cls, col ): return cls.__modelHeaderData[ col ]
    def modelData( self, col ): return self.__modelData[ col ]

    def afterLoad( self ):
        pass

    def afterUpdate( self ):
        pass

    def __repr__(self): return f'{str(self.UID)} {self.name} {str( self.typeUID )}'

###################################################################################

class CGraf_NO( CNetObj ):
    def __init__( self, name="", parent=None):
        super().__init__( name = name, parent = parent )
        self.nxGraf = None

    def afterLoad( self ):
        # create nxGraf from childNodes
        pass

class CGrafNode_NO( CNetObj ):
    def __init__( self, name="", parent=None):
        super().__init__( name = name, parent = parent )

    def nxGraf(self):
        return self.grafNode().nxGraf

    def grafNode(self):
        r = Resolver('name')
        return r.get(self, '../../')

    def afterLoad( self ):
        # graf = queryNode(self, '../../', CGraf_NO)

        # for attr
        #     graf.nxGraf().nodes[ name ][ attr ] = val
        # # create nxGraf from childNodes
        pass

class CGrafEdge_NO( CNetObj ):
    def __init__( self, name="", parent=None):
        super().__init__( name = name, parent = parent )

def registerNetNodeTypes():
    reg = CNetObj_TypeManager.registerType
    reg( CNetObj )
    reg( CGraf_NO )
    reg( CGrafNode_NO )
    reg( CGrafEdge_NO )
