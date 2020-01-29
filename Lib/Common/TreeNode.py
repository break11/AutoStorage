
import weakref

class CTreeNode:
    PS = "/" # Path Splitter
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
        l = path.split( CTreeNode.PS )
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
    
    def path( self ):
        l = []
        obj = self
        while obj.parent is not None:
            l.append( obj.name )
            obj = obj.parent
        
        return CTreeNode.PS + CTreeNode.PS.join( reversed(l) )

    def __repr__(self): return f"<TreeNode Name={self.name} Class={self.__class__.__name__}>"

