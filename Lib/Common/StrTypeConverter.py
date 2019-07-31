
from . import StrConsts as SC

class CStrTypeConverter:
    __TypeLetters = {
                    int: "i",
                    str: "s",
                    float: "f",
                    }
    __LettersType = {}
    for k,v in __TypeLetters.items():
        __LettersType[ v ] = k

    std_types        = __TypeLetters.keys()
    std_type_letters = __TypeLetters.values()

    __TypeLettersU = {}    #type:ignore
    __LettersTypeU = {}    #type:ignore
    user_types = []        #type:ignore
    user_type_letters = [] #type:ignore

    @classmethod
    def registerUserType( cls, typeChar, typeClass ):
        assert typeChar not in cls.user_type_letters
        assert typeClass not in cls.user_types
        assert hasattr( typeClass, "fromString" )
        assert hasattr( typeClass, "toString" )

        cls.__TypeLettersU[ typeClass ] = typeChar
        cls.__LettersTypeU[ typeChar  ] = typeClass
        cls.user_types.append( typeClass )
        cls.user_type_letters.append( typeChar )

    @classmethod
    def ValFromStr( cls, s ):
        typeSign = s[0]
        val = s[1::]

        if typeSign in cls.std_type_letters:
            t = cls.__LettersType.get( typeSign )
            return (t)(val)

        elif typeSign in cls.user_type_letters:
            t = cls.__LettersTypeU.get( typeSign )
            return t.fromString( val )

        else:
            print( f"{SC.sWarning} Unsupport type = {typeSign} value = {val} for converting from String!" )
            
    @classmethod
    def ValToStr( cls, val ):
        t = type( val )

        if t in cls.std_types:
            typeSign = cls.__TypeLetters.get( t )
            return typeSign + str( val )

        elif t in cls.user_types:
            typeSign = cls.__TypeLettersU.get( t )
            return typeSign + val.toString()

        else:
            print( f"{SC.sWarning} Unsupport type = {t} value = {val} for converting to String!" )
        
    @classmethod
    def DictToStr( cls, d ):
        d1 = {}
        for k, v in d.items():
            d1[ k ] = cls.ValToStr( v )
        return d1

    @classmethod
    def DictFromStr( cls, d ):
        d1 = {}
        for k, v in d.items():
            d1[ k ] = cls.ValFromStr( v )
        return d1

    @classmethod
    def DictFromBytes( cls, d ):
        d1 = {}
        for k, v in d.items():
            d1[ k.decode() ] = cls.ValFromStr( v.decode() )
        return d1
