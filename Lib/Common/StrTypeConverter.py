
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

    @classmethod
    def ValFromStr( cls, s ):
        typeSign = s[0]
        val = s[1::]
        t = cls.__LettersType.get( typeSign )
        if not t:
            print( f"{SC.sWarning} Unsupport type = {typeSign} for converting from String!" )
            return

        return (t)(val)

    @classmethod
    def ValToStr( cls, val ):
        t = type( val )
        typeSign = cls.__TypeLetters.get( t )
        if not typeSign:
            print( f"{SC.sWarning} Unsupport type = {t} for converting to String!" )
            return

        return typeSign + str( val )
        
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
