class СStrProps_Meta(type):
    def __init__( cls, className, baseClasses, dictOfMethods):
        for k, v in dictOfMethods.items():
            if k.startswith( "__" ): continue
            if v is not None: continue
            setattr( cls, k, k )