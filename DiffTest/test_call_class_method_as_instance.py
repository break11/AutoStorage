class CTest:
    @classmethod
    def test( cls ):
        print( cls, type( cls ), id(cls) )

CTest.test()

print( "---------------------" )

A = CTest()
A.test()