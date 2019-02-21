
import unittest

import sys
import os

sys.path.append( os.path.abspath(os.curdir)  )

from  Lib.Common.TreeNode import CTreeNode, CTreeNodeCache

rootNode = CTreeNode( name = "rootNode" )

c1_Node   = CTreeNode( parent = rootNode, name = "c1" )
c1_1_Node = CTreeNode( parent = c1_Node,  name = "c1_1" )
c1_2_Node = CTreeNode( parent = c1_Node,  name = "c1_2" )

c2_Node   = CTreeNode( parent = rootNode, name = "c2" )
c2_1_Node = CTreeNode( parent = c2_Node,  name = "c2_1" )
c2_2_Node = CTreeNode( parent = c2_Node,  name = "c2_2" )

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
        self.assertEqual( CTreeNode.resolvePath( obj = c1_Node, path = "/c1_1" ) , c1_1_Node )
        self.assertEqual( CTreeNode.resolvePath( obj = c1_1_Node, path = ".." ) , c1_Node )
        self.assertEqual( CTreeNode.resolvePath( obj = c1_1_Node, path = "../../.." ) , None )
        self.assertEqual( CTreeNode.resolvePath( obj = c1_1_Node, path = "../../c2/c2_1" ) , c2_1_Node )

    def test_TreeNodeCache(self):
        c1_1_cache = CTreeNodeCache( baseNode = c2_2_Node, path = "../../c1/c1_1" )
        self.assertEqual( c1_1_cache(), c1_1_Node )

        none_cache = CTreeNodeCache( baseNode = c2_2_Node, path = "../../c1/c1_1/Non_Exist_Obj" )
        self.assertEqual( none_cache(), None )

if __name__ == '__main__':
    unittest.main()