
from .StrConsts import SC

class CStrTypeConverter:
    s_fromString = 'fromString'
    from_str_funcs = {} #type:ignore
    
    @classmethod
    def registerType( cls, typeClass, from_str_func ):
        assert typeClass.__name__ not in cls.from_str_funcs

        cls.from_str_funcs[ typeClass.__name__ ] = from_str_func

    @classmethod
    def registerStdType( cls, typeClass ):
        cls.registerType( typeClass, from_str_func=typeClass )

    @classmethod
    def registerUserType( cls, typeClass ):
        cls.registerType( typeClass, from_str_func=typeClass.fromString )

    @classmethod
    def clear( cls): cls.from_str_funcs.clear()

    ###################

    @classmethod
    def ValFromStr( cls, typeClassName, s ):
        if typeClassName in cls.from_str_funcs:
            obj = cls.from_str_funcs[ typeClassName ]( s )
            return obj
        else:
            print( f"{SC.sWarning} Unsupport type = {typeClassName} value = {s} for converting from String!" )
            
    @classmethod
    def ValToStr( cls, val ):
        typeClass = type( val )
        if typeClass.__name__ in cls.from_str_funcs:
            return str( val )
        else:
            print( f"{SC.sWarning} Unsupport type = {typeClass.__name__} value = {val} for converting to String!" )

    ###################

    @classmethod
    def DictToStr( cls, d ):
        d1 = {}
        for k, v in d.items():
            d1[ k ] = cls.ValToStr( v )
        return d1

    @classmethod
    def DictFromStr( cls, d, def_props={} ):
        d1 = {}
        for k, v in d.items():
            typeClass = type( def_props[k] ) if k in def_props else str
            d1[ k ] = cls.ValFromStr( typeClass.__name__, v )
        return d1

