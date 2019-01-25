class Node:
    def __init__(self, identifier):
        self.__identifier = identifier
        self.__children = []

    @property
    def identifier(self):
        return self.__identifier

    @property
    def children(self):
        return self.__children

    def add_child(self, identifier):
        self.__children.append(identifier)

# N = Node( "test" )

# N.children = 125
# print( N.children )

str = ""
if not str:
    print( "not str" )