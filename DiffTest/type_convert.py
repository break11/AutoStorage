

from enum import Enum, auto

class MyType( Enum ):
    def __init__(self, *args, **kwargs):
        print( "11111111111111" )
    a = auto
    b = auto
    c = auto

    # def __call__(self, *args, **kwargs):
    #     print( "11111111111111" )

(MyType)(a)