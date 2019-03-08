
import weakref

# место хранения всех прокси элементов, при удалении из этого контейнера элемент должен уничтожиться
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

    def __init__( self, netObj ):
        print( "proxy init", netObj )
        self.netObj = weakref.ref( netObj )

        parent = netObj.parent
        self.parentProxy = weakref.ref( gProxys.get( parent.UID ) ) if parent else None

        gProxys[ netObj.UID ] = self

        self.__childProxy = [] # список netObj ID дочерних прокси элементов, сами прокси элементы хранятся в gProxy
        self.bChildExpanded = False

    def __del__( self ):
        print( "proxy done", self.netObj() )
        for UID in list(self.__childProxy):
            self.__removeChildProxy( UID )
        self.__childProxy.clear()

        # if self.parentProxy is not None and self.parentProxy():
        #     self.parentProxy().removeChildProxy( self )

    #################################################################

    def getChildProxy( self, indexInParent ):
        self.checkChildren()
        return gProxys.get( self.__childProxy[ indexInParent ] )
    
    def appendChildProxy( self, proxy ):
        self.__childProxy.append( proxy.netObj().UID )

    def __removeChildProxy( self, UID ):
        # if UID in self.__childProxy:
        self.__childProxy.remove( UID )
        del gProxys[ UID ]

    def removeChildProxy( self, proxy ):
        UID = proxy.netObj().UID
        self.__removeChildProxy( UID )

    def getChildProxyCount( self ):
        self.checkChildren()
        return len( self.__childProxy )

    def getChildProxyIndex( self, proxy ):
        return self.__childProxy.index( proxy.netObj().UID )

    #################################################################

    def checkChildren(self):
        if not self.bChildExpanded:
            for child in self.netObj().children:
                self.__childProxy.append( CNetObj_Proxy.queryProxy_from_NetObj( child ).netObj().UID )
            self.bChildExpanded = True

    