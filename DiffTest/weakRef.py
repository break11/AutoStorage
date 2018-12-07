
w = weakref.WeakSet()
# w = set()

def test():
    pass

def test2():
    pass

class A:
    @classmethod
    def test3(self):
        pass

a = A()

print( len(w) )
w.add( test )
print( len(w) )
w.add( test2 )
print( len(w) )
w.add( A.test3 )
print( len(w) )
w.add( weakref.WeakMethod(A.test3) )
print( len(w) )
w.add( weakref.WeakMethod( a.test3 ) )
print( len(w) )
print( A.test3, "************8" )
