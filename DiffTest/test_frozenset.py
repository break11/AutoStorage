for i in range(100):
    f = frozenset( ("nRD", "n0") )
    r = frozenset( ("n0", "nRD") )
    print( f, r, f == r, tuple(f), tuple(r)  )