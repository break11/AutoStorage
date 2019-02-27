
import weakref

class CTreeNode:
    ##########################

    @property
    def children( self ):
        return self.__children

    def clearChildren( self ):
        self.__children.clear()
        self.__children_dict.clear()

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
        self.__parent.__children.append( self )
        self.__parent.__children_dict[ self.name ] = self

    def clearParent( self ):
        if self.__parent is None: return
        self.__parent.__children.remove( self )
        del self.__parent.__children_dict[ self.name ]
        self.__parent = None
    ##########################

    def __init__( self, parent=None, name=None ):
        if parent is not None:
            assert parent.childByName( name ) is None, f"Can not create tree element with duplicate name='{name}'"

        self.name = name

        self.__parent = None
        self.parent = parent

        self.__children = []
        self.__children_dict = {}

    def childByName( self, name ):
        return self.__children_dict.get( name )

    @classmethod
    def resolvePath( cls, obj, path ):
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

class CTreeNodeCache:
    def __init__( self, baseNode, path):
        self.baseNode = weakref.ref( baseNode )
        self.path = path
        self.__cache = None

    def __call__( self ):
        if self.__cache is None:
            self.__cache = CTreeNode.resolvePath( self.baseNode(), self.path )
            if self.__cache: self.__cache = weakref.ref( self.__cache )
        return self.__cache() if self.__cache else None
