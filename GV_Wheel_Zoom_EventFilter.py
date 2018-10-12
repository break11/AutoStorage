
from PyQt5.QtCore import ( Qt, QObject, QEvent, QTimer, QRectF )
from PyQt5.QtWidgets import ( QGraphicsView )

from GuiUtils import *

class CGV_Wheel_Zoom_EventFilter(QObject):
    __gView = None
    __tmFitOnFirstShow = QTimer()
    ZoomFactor = 1.15

    def __init__(self, gView):
        super(CGV_Wheel_Zoom_EventFilter, self).__init__(gView)
        self.__gView = gView
        gView.installEventFilter( self )

        self.__tmFitOnFirstShow.setInterval( 100 )
        self.__tmFitOnFirstShow.setSingleShot( True )
        self.__tmFitOnFirstShow.timeout.connect( self.fitToPage )
        self.__tmFitOnFirstShow.start()

    def eventFilter(self, object, event):
        if event.type() == QEvent.KeyPress:
            if event.modifiers() & Qt.AltModifier:
                self.__gView.setDragMode( QGraphicsView.DragMode.ScrollHandDrag )

        if event.type() == QEvent.KeyRelease:
            if event.modifiers() & Qt.ControlModifier:
                if event.key() == Qt.Key_Left:
                    self.__gView.rotate( -90 )
                if event.key() == Qt.Key_Right:
                    self.__gView.rotate( 90 )
            
            if not ( event.modifiers() & Qt.AltModifier):
                self.__gView.setDragMode( QGraphicsView.DragMode.RubberBandDrag )

        if event.type() == QEvent.Wheel:
            if event.modifiers() & Qt.ControlModifier:
                if event.angleDelta().y() > 0:
                    self.zoomIn()
                else:
                    self.zoomOut()
                return True
        return False

    def fitToPage(self):
        gvFitToPage( self.__gView )

    def zoomIn(self):
        self.__gView.scale( self.ZoomFactor, self.ZoomFactor )

    def zoomOut(self):
        self.__gView.scale( 1 / self.ZoomFactor, 1 / self.ZoomFactor )


