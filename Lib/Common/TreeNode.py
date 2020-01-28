
import weakref

class CTreeNode:
    ##########################

    @property
    def children( self ):
        return self.__children_dict.values()

    def clearChildren( self ):
        self.__children_dict.clear()

    def childCount( self ):
        return len( self.__children_dict )

    ##########################
    @property
    def parent( self ):
        return self.__parent
    
    @parent.setter
    def parent( self, value ):
        if value is None:
            self.clearParent()
            return
        
        self.__parent = value
        self.__parent.__children_dict[ self.name ] = self

    def clearParent( self ):
        if self.__parent is None: return
        del self.__parent.__children_dict[ self.name ]
        self.__parent = None
    ##########################

    def __init__( self, parent=None, name=None ):
        if parent is not None:
            assert parent.childByName( name ) is None, f"Can not create tree element with duplicate name='{name}'"

        self.name = name

        self.__parent = None
        self.parent = parent

        self.__children_dict = {}

    def childByName( self, name ):
        return self.__children_dict.get( name )
    
    def rename( self, newName ):
        oldName = self.name
        self.name = newName

        if self.parent is None: return

        self.parent.__children_dict[ newName ] = self
        del self.parent.__children_dict[ oldName ]

    @classmethod
    def resolvePath( cls, obj, path ):
        if obj is None: return None
        l = path.split("/")
        l = [ item for item in l if item != "" ]
        dest = obj
        for item in l:
            if item == "..":
                dest = dest.parent
            else:
                dest = dest.childByName( item )
            if dest is None:
                break
        return dest

    def __repr__(self): return f"<TreeNode Name={self.name} Class={self.__class__.__name__}>"

##################################################################################

##remove##

from Lib.Net.NetObj_Manager import CNetObj_Manager

class CTreeNodeCache:
    def __init__( self, path, baseNode = None ):
        # baseNode - должна быть типа CNetObj, но для исключения перекрестных ссылок проверяем, что по ошибке не был передан экземпляр CTreeNodeCache
        # такое возможно из-за существования хелперных функций возвращающих CTreeNodeCache, которым дополнительно надо вызвать __call__
        assert not isinstance( baseNode, CTreeNodeCache )

        self.baseNode = weakref.ref( baseNode ) if baseNode is not None else None
        self.path = path
        self.__cache = None

    def __call__( self ):
        if (self.__cache is None) or (self.__cache() is None):
            baseNode = self.baseNode() if self.baseNode is not None else CNetObj_Manager.rootObj
            # self.__cache = CTreeNode.resolvePath( self.baseNode(), self.path )
            self.__cache = CTreeNode.resolvePath( baseNode, self.path )
            if self.__cache: self.__cache = weakref.ref( self.__cache )
        return self.__cache() if self.__cache else None
