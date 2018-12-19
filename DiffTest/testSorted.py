
s = { b'30', b'100', b'10' }

for v in s:
    print( v.decode(), type( v.decode() ) )

print( sorted( s, key = lambda x: int(x.decode()) ) )