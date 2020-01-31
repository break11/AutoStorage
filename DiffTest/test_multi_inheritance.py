class Base1_parent():
    def __init__(self):
        print( "init Base1_parent" )
        super().__init__(2, 3)

class Base1( Base1_parent ):
    def __init__(self, a):
        print( "init Base1", a )
        super().__init__()

class Base2():
    def __init__(self, b, c):
        print( "init Base2", b, c )
        # super().__init__()

    def func(self):
        print("func")


class Child( Base1, Base2 ):
    def __init__(self):
        Base1.__init__( self, 1 )
        Base2.__init__( self, 1, 2 )


        # super().__init__( 1 )
        # super().__init__( 1, 2 )
        # super(Base1, self).__init__( 2, 3 )
        print( "init Child" )
        # super( Child, self ).__init__( 1 )
        self.func()

Child()