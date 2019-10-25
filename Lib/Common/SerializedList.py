
TS  = "," # Task Splitter

class CSerializedList:
    element_type = None
    def __init__( self, elementList=None ):
        assert self.element_type is not None, "Need to specify type of list elements!"
        self.elementList = elementList if elementList is not None else []

    def __str__( self ): return self.toString() # return string list of elements | "element,element"

    def __call__( self ): return self.elementList # return list of type element_type | [ element, element ]
        
    @classmethod
    def fromString( cls, data ):
        if not data:
            return cls.element_type()

        rL = []
        l = data.split( TS )
        for s_element in l:
            if cls.element_type == str:
                element = s_element
            else:
                element = cls.element_type.fromString( s_element )
            rL.append( element )
        return cls( elementList=rL )

    def toString( self ):
        # if type(self) == str:
        #     return self
        return TS.join( map(str, self.elementList) )

############

class CStrList( CSerializedList ):
    element_type = str #type: ignore
