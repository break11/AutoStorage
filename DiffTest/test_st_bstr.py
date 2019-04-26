
a = "aaa \n bbb"
b = b"aaa \n bbb"

c = f" b={b} "

d = "'aaa \\n  bbb'"

print( c, c.index("\\"), a.index("\\") )
# print( c )
# print( a )