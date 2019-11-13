
from .StrConsts import SC

class CStrTypeConverter:
    s_fromString = 'fromString'
    from_str_funcs = {} #type:ignore
    
    @classmethod
    def registerType( cls, typeClass ):
        assert typeClass not in cls.from_str_funcs

        if hasattr( typeClass, cls.s_fromString ):
            cls.from_str_funcs[ typeClass ] = typeClass.fromString
        else:
            cls.from_str_funcs[ typeClass ] = typeClass

    ###################

    @classmethod
    def ValFromStr( cls, typeClass, s ):
        if typeClass in cls.from_str_funcs:
            obj = cls.from_str_funcs[ typeClass ]( s )
            return obj
        else:
            print( f"{SC.sWarning} Unsupport type = {typeClass.__name__} value = {s} for converting from String!" )
            
    @classmethod
    def ValToStr( cls, val ):
        typeClass = type( val )
        if typeClass in cls.from_str_funcs:
            return str( val )
        else:
            print( f"{SC.sWarning} Unsupport type = {typeClass.__name__} value = {val} for converting to String!" )
