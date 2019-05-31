
from enum import Enum, auto

class EWidthType( Enum ):
    Narrow = auto()
    Wide   = auto()

    @classmethod
    def test(cls): print( "test" )

print( EWidthType[ "test" ] )
EWidthType.test()

# class FFF:
#     def __init__(self):
#         self.r = 1


# class Tree:
#     test123 = "1"
#     def __init__(self, left: "Tree", right: "Tree", top: "FFF") -> None:
#         self.left = left
#         self.right = right
#         top.r



# from __future__ import annotations
 
# class Tree:
#     def __init__(self, left: Tree, right: Tree) -> None:
#         self.left = left
#         self.right = right

# a = Tree( 1, 2 )

# print( Tree, a )

# dir( test )

# class Base:
#     def testF( self ):
#         self.virt()

#     def virt( self ):
#         print( "base virt" )
#         pass

# class Child( Base ):
#     def virt( self ):
#         # super().virt()
#         print( "child virt" )

# A = Child()
# A.testF()


# from copy import *

# s1 = "padla"
# s2 = (s1 + '.')[:-1]
# # s2 = s1

# h1 = hash( s1 )
# h2 = hash( s2 )

# print( id(s1), id(s2) )
# print( h1, h2, h1==h2 )

# import hashlib
# import sys

# print( int(hashlib.md5( s1.encode() ).hexdigest(), 16) )
# print( sys.getsizeof( int(4) ) )
# print( sys.getsizeof( int(hashlib.sha512( s2.encode() ).hexdigest(), 16) ) )
# print( hashlib.sha1( s2.encode() ).digest() )
