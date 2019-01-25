
class a:
    @classmethod
    def test(cls):
        print( "1" )

class b(a):
    @classmethod
    def test(cls):
        super().test()
        print( "2" )

b.test()