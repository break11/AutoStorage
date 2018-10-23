

class A(type):
    # pass
    def __new__(cls, className, baseClasses, dictOfMethods):
        return type.__new__(cls, className, baseClasses, dictOfMethods)

    def __init__( cls, className, baseClasses, dictOfMethods):
        print( "1111111111111111" )

    def __del__( cls ):

        print( "222222222222222222222222222222222" )
        # super().__del__( cls )
        # cls.options = {}
        # print( "print!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!11" )

# 
    # def __del__( cls ):
    #     cls.options = {}
    #     print( "2222222222222222222222222222222222" )

class SettingsManager( object, metaclass = A ):
    # def __init__(self):
    pass

# print( type(SettingsManager) )
