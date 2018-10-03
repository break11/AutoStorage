
from PyQt5.QtCore import ( Qt, QObject, QEvent, QTimer, QRectF )

class CGV_Wheel_Zoom_EventFilter(QObject):
    __gView = None
    __tmFitOnFirstShow = QTimer()

    def __init__(self, gView):
        super(CGV_Wheel_Zoom_EventFilter, self).__init__(gView)
        self.__gView = gView

        self.__tmFitOnFirstShow.setInterval( 50 )
        self.__tmFitOnFirstShow.setSingleShot( True )
        self.__tmFitOnFirstShow.timeout.connect( self.fitToPage )
        self.__tmFitOnFirstShow.start()

        # увеличение размера области просмотра GraphicsView для более удобной навигации по сцене
        tl = gView.sceneRect().topLeft()
        br = gView.sceneRect().bottomRight()
        tl = tl  + ( tl-br ) / 4
        br = br  + ( br-tl ) / 4
        gView.setSceneRect( QRectF( tl, br ) )

    def eventFilter(self, object, event):
        if event.type() == QEvent.MouseButtonPress:
            if event.modifiers() & Qt.ControlModifier:
                self.fitToPage()

        if event.type() == QEvent.Wheel:
            if event.modifiers() & Qt.ControlModifier:
                if event.angleDelta().y() > 0:
                    self.__gView.scale(1.15, 1.15)
                else:
                    self.__gView.scale(1/1.15, 1/1.15)
                return True
        return False

    def fitToPage(self):
        self.__gView.fitInView( self.__gView.scene().sceneRect(), Qt.KeepAspectRatio )


