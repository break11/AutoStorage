

class CTest():
    def __init__( self ):
        super().__init__()
        self.testField = "This Test Field"
        self.d = {}

    def __getitem__( self, key ):
        return self.d[ key ]

    def __setitem__( self, key, value ):
        self.d[ key ] = value

    def __delitem__( self, key ):
        del self.d[ key ]

    # def __getattr__(self, name):
    #     print( "__getattr__", name )
    #     return name

    # def __setattr__(self, name, value):
    #     if name != "testField_21":
    #         super().__setattr__( name, value)
    #     print( "__setattr__", name, value )
    #     # self.d[ name ] = value

a = CTest()

a[ "test123" ] = "123"
print( a[ "test123" ] )

del a[ "test123" ]
print( a[ "test123" ] )

# print( a.testField, a.testField_21, "***" )
# a.testField = 1
# a.testField_21 = 35 # type: ignore