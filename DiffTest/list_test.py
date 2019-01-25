
## b = c
def a(b):
    b[0] = 2
    b = [1,2,3]
    print( b )

c = [3]
print( c )
a(c)
print( c )