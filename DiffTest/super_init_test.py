class CTest:
    testField = 1
    def testFunc( self ): pass

    def __init__( self ):
        print( self.__dict__ )

        super().__init__()
        self.A = 2
        self.testField = 3

        print( self.__dict__ )

a = CTest()
print( CTest.__dict__ )

