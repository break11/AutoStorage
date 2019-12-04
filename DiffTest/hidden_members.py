class CTest:
    publicClassField = 1
    __privateClassField = 2
    def __init__( self ):
        self.publicField = 3
        self.__privateField = 4

print( vars(CTest) )
print( CTest._CTest__privateClassField )

print( "-----------------------------------" )

A = CTest()
print( vars( A ) )
print( A._CTest__privateField )