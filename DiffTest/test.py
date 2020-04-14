
i = 0
if not i:
    print( "111111111", bool("False") )

# class A:
#     def __init__(self):
#         print( self.EnumType )

# class B( A ):
#     EnumType = "Test_111111111111"

# b = B()

# # print( str( True ) )

# v = 1

# print( v.__class__.__name__ )

# class CTest:
#     a = 1
#     print( a )

# v = CTest()
# # print( v.__class__.__name__ )

# CTest(  )

# (CTest)(1)
# a = eval( "a = CTest();a=" )()


# class A:
#     test = [1, 2 ,3]
#     def __eq__( self, other ):
#         return self.test == other.test

# a = A()
# b = A()

# print( a == b )

# from enum import Enum, IntEnum

# class ESomeEnum( Enum ):
#     Narrow = 1
#     Wide   = 2
#     N      = 1
#     W      = 2

# print( ESomeEnum.Narrow == ESomeEnum.N )
# print( ESomeEnum.N.name )
# print( ESomeEnum["N"] )

# class EIntEnum( Enum ):
#     H = 1
#     L = 0

# print( EIntEnum.H == 1 )


# class СStrProps_Meta(type):
#     def __init__( cls, className, baseClasses, dictOfMethods):
#         for k, v in dictOfMethods.items():
#             if not k.startswith( "__" ):
#                 setattr( cls, k, k )

# class СStrProps( metaclass = СStrProps_Meta ):
#     one = None
#     two = None

# print( СStrProps.one )

# class Test():
#     A = None

# b = "string"

# Test.b = 1

# print( Test.b )

# b = None 
# b = isinstance(b, type(None))
# print( b, type(None) )

# from enum import Enum, auto

# class ESide( Enum ):
#     Left            = auto()
#     Right           = auto()
#     ChargeSideLeft  = Right # ChargeSideLeft - указывает положение "минуса", т.е. "плюс" справа. У челнока "плюс" в передней части.
#     ChargeSideRight = Left  # поэтому при ChargeSideLeft челнок необходимо располагать вектором в правый сектор.

# print( ESide.ChargeSideLeft )
# print( ESide[ "ChargeSideLeft" ] )


# l = [1,2,3,3,2,1]

# print( l.index(3,3) )

# from enum import Enum, auto

# class EWidthType( Enum ):
#     Narrow = auto()
#     Wide   = auto()

#     @classmethod
#     def test(cls): print( "test" )

# print( EWidthType[ "test" ] )
# EWidthType.test()

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
