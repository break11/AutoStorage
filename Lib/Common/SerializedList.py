
import re

TS  = "," # Task Splitter
split_pattern = " ,|,| |:|-"

class CSerializedList:
    element_type = None
    def __init__( self, elementList=None ):
        assert self.element_type is not None, "Need to specify type of list elements!"
        self.elementList = elementList if elementList is not None else []

    def __str__( self ): return self.toString() # return string list of elements | "element,element"

    def __call__( self ): return self.elementList # return list of type element_type | [ element, element ]
        
    def __getitem__( self, key ): return self.elementList[ key ]

    def clear( self ): self.elementList.clear()

    def isEmpty( self ): return len( self.elementList ) == 0

    @classmethod
    def fromString( cls, data ):
        if not data:
            return cls( elementList=[] )

        rL = []
        l = re.split( split_pattern, data )
        if cls.element_type == str:
            rL = l
        else:
            for s_element in l:
                element = cls.element_type.fromString( s_element )
                rL.append( element )
        return cls( elementList=rL )

    def toString( self ):
        return TS.join( map(str, self.elementList) )

    def count(self): return len( self.elementList )

############

class CStrList( CSerializedList ):
    element_type = str #type: ignore
