a = (1, 2)
b = (2, 1)

fs_a = frozenset(a)
fs_b = frozenset(b)

print ( a[0], fs_a )
print ( b[0], fs_b )

t_a = tuple(fs_a)
t_b = tuple(fs_b)

print (t_a, t_b)
