from weakref import WeakSet, WeakMethod

class Test():
    def __init__(self, name):
        self.name = name
    def __del__(self):
        # print (self.name)
        pass

    def func(self):
        pass

s = WeakSet()

a, b, c = Test("a"), Test("b"), Test("c")
s.add( a )
s.add( b )
print( s.data )
del a
print("======================")
print( s.data )