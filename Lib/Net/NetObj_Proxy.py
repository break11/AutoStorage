
import weakref

gProxys = {} # type:ignore

class CNetObj_Proxy:
    bChildExpanded = False

    @classmethod
    def queryProxy_from_NetObj( cls, netObj ):
        proxy = cls.proxy_from_NetObjID( netObj.UID )
        if proxy:
            return proxy
        return CNetObj_Proxy( netObj )

    @classmethod
    def proxy_from_NetObjID( cls, UID ):
        return gProxys.get( UID )

    @classmethod
    def removeProxy( cls, UID ):
        del gProxys[ UID ]

    def __init__( self, netObj ):
        print( "proxy init", netObj )
        self.netObj = weakref.ref( netObj )

        parent = netObj.parent
        self.parentProxy = weakref.ref( gProxys.get( parent.UID ) ) if parent else None

        gProxys[ netObj.UID ] = self

        self.childProxy = []
        self.bChildExpanded = False

    def __del__( self ):
        print( "proxy done", self.netObj() )
        # for 
        self.childProxy.clear()

    def getChildProxy( self, indexInParent ):
        self.checkChildren()
        return self.childProxy[ indexInParent ]

    def getChildCount( self ):
        self.checkChildren()
        return len( self.childProxy )

    def checkChildren(self):
        if not self.bChildExpanded:
            for child in self.netObj().children:
                self.childProxy.append( CNetObj_Proxy.queryProxy_from_NetObj( child ) )
            self.bChildExpanded = True

    