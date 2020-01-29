#!/usr/bin/python3.7

import unittest

import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )

from  Lib.Common.TreeNode import CTreeNode
from  Lib.Common.TreeNodeCache import CTreeNodeCache

rootNode = CTreeNode( name = "rootNode" )

c1_Node   = CTreeNode( parent = rootNode, name = "c1" )
c1_1_Node = CTreeNode( parent = c1_Node,  name = "c1_1" )
c1_2_Node = CTreeNode( parent = c1_Node,  name = "c1_2" )

c2_Node   = CTreeNode( parent = rootNode, name = "c2" )
c2_1_Node = CTreeNode( parent = c2_Node,  name = "c2_1" )
c2_2_Node = CTreeNode( parent = c2_Node,  name = "c2_2" )

c3_Node   = CTreeNode( parent = rootNode, name = "c3" )
c3_1_Node = CTreeNode( parent = c3_Node,  name = "c3_1" )

class TestTreeNode(unittest.TestCase):
    def test_parent(self):
        self.assertEqual( c1_1_Node.parent , c1_Node )

    def test_children(self):
        self.assertTrue( c1_1_Node in c1_Node.children )

    def test_childByName(self):
        self.assertEqual( c1_Node.childByName( "c1_1" ) , c1_1_Node )
        self.assertEqual( c2_Node.childByName( "c2_1" ) , c2_1_Node )

        self.assertEqual( c2_Node.childByName( "c2_1___NOT" ) , None )

    def test_resolvePath(self):
        self.assertEqual( CTreeNode.resolvePath( obj = c1_Node, path = "" ) , c1_Node )
        self.assertEqual( CTreeNode.resolvePath( obj = c1_Node, path = "//" ) , c1_Node )
        self.assertEqual( CTreeNode.resolvePath( obj = c1_Node, path = "/" ) , c1_Node )

        self.assertEqual( CTreeNode.resolvePath( obj = c1_Node, path = "/c1_1" ) , c1_1_Node )
        self.assertEqual( CTreeNode.resolvePath( obj = c1_1_Node, path = ".." ) , c1_Node )
        self.assertEqual( CTreeNode.resolvePath( obj = c1_1_Node, path = "../../.." ) , None )
        self.assertEqual( CTreeNode.resolvePath( obj = c1_1_Node, path = "../../c2/c2_1" ) , c2_1_Node )

    def test_TreeNodeCache(self):
        CTreeNodeCache.rootObj = rootNode # type:ignore

        c1_1_cache = CTreeNodeCache( basePath = c2_2_Node.path(), path = "../../c1/c1_1" )
        self.assertEqual( c1_1_cache(), c1_1_Node )

        # не несуществующий объект кеш должен вернуть None
        none_cache = CTreeNodeCache( basePath = c2_2_Node.path(), path = "../../c1/c1_1/Non_Exist_Obj" )
        self.assertEqual( none_cache(), None )

        # после того как объект которого не было был создан - кеш должен вернуть его
        Non_Exist_Obj = CTreeNode( parent = c1_1_Node,  name = "Non_Exist_Obj" )
        self.assertEqual( none_cache(), Non_Exist_Obj )

        # если объект был удален - кеш снова должен вернуть None
        Non_Exist_Obj.parent = None
        del Non_Exist_Obj
        self.assertEqual( none_cache(), None )

        # если объект создан вновь - кеш снова возвращает его (новосозданный объект по заданному пути)
        Non_Exist_Obj = CTreeNode( parent = c1_1_Node,  name = "Non_Exist_Obj" )
        self.assertEqual( none_cache(), Non_Exist_Obj )

        ##############################
        # проверка корректной работы подмены парента базового объекта для кеша

        CTreeNodeCache.rootObj = c1_Node # type:ignore

        c1_1_cache = CTreeNodeCache( path = "/c1_1" )
        self.assertEqual( c1_1_cache(), c1_1_Node )

        CTreeNodeCache.rootObj = rootNode # type:ignore

        c1_1_cache = CTreeNodeCache( path = "/c1/c1_1" )
        self.assertEqual( c1_1_cache(), c1_1_Node )

    def test_rename( self ):
        self.assertEqual( CTreeNode.resolvePath( obj = rootNode, path = "/c3" ) , c3_Node )
        self.assertEqual( CTreeNode.resolvePath( obj = c3_Node, path = "/c3_1" ) , c3_1_Node )
        self.assertEqual( "c3", c3_Node.name )
        c3_Node.rename( "c3_new" )
        self.assertEqual( CTreeNode.resolvePath( obj = rootNode, path = "/c3_new" ) , c3_Node )
        self.assertEqual( CTreeNode.resolvePath( obj = c3_Node, path = "/c3_1" ) , c3_1_Node )
        self.assertEqual( "c3_new", c3_Node.name )

if __name__ == '__main__':
    unittest.main()
