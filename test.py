
dir( test )

class Base:
    def testF( self ):
        self.virt()

    def virt( self ):
        print( "base virt" )
        pass

class Child( Base ):
    def virt( self ):
        # super().virt()
        print( "child virt" )

A = Child()
A.testF()


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
