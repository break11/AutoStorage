from anytree import Node, RenderTree

udo = Node("Udo")
marc = Node("Marc")
lian = Node("Lian", parent=marc)

print(RenderTree(udo))
print(RenderTree(marc))

marc.parent = udo
print(RenderTree(udo))

print( marc.is_root )
print( udo.children )
marc.parent = None
print( marc.is_root )
print( udo.children )


print(RenderTree(udo))
print(RenderTree(marc))

print( lian.children == () )
