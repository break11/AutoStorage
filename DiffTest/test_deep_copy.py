from copy import deepcopy
gd = {"pos":1, "edge":"", "dir":1}

class Base():
    def __init__(self, d = {}):
        self.d = d

class Test(Base):
    def __init__(self, d = deepcopy( gd ) ):
        super().__init__( d = d )

a = Test()
b = Test()
print ( f"1: gd = { gd } {id(gd)},    a = { a.d } {id(a.d)}     b = { b.d } {id(b.d)}" )

b.d["pos"] = 10
print ( f"2: gd = { gd } {id(gd)},    a = { a.d } {id(a.d)}     b = { b.d } {id(b.d)}" )
# b.d[0] = "b"
# print ( f"3: gd = { gd } {id(gd)},    a = { a.d } {id(a.d)}     b = { b.d } {id(b.d)}" )