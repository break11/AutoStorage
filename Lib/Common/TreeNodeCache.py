import weakref

from Lib.Common.TreeNode import CTreeNode

class CTreeNodeCache:
    rootObj = None
    def __init__( self, path, basePath = CTreeNode.PS ):
        self.path = path
        self.basePath = basePath

        self.__baseNode = None
        self.__cache = None

    def __resolveToWeakRef( self, baseNode, obj_path, obj_ref ):
        assert baseNode is not None

        if (obj_ref is None) or (obj_ref() is None):
            obj = CTreeNode.resolvePath( baseNode, obj_path )
            if obj: obj_ref = weakref.ref( obj )

        return obj_ref

    def __call__( self ):
        self.__baseNode = self.__resolveToWeakRef( CTreeNodeCache.rootObj, self.basePath, self.__baseNode )

        if self.__baseNode is None: return

        self.__cache = self.__resolveToWeakRef( self.__baseNode(), self.path, self.__cache )

        return self.__cache() if self.__cache else None
