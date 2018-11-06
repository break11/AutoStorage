
from PyQt5.QtCore import ( Qt, QObject, QEvent, QTimer, QRectF )
from PyQt5.QtWidgets import ( QGraphicsView )

from .GuiUtils import *

class CGV_Wheel_Zoom_EventFilter(QObject):
    ZoomFactor = 1.15

    def __init__(self, gView):
        super(CGV_Wheel_Zoom_EventFilter, self).__init__( parent = gView )
        self.__gView = gView
        self.__gView.installEventFilter( self )

        self.__moveStartX = 0
        self.__moveStartY = 0
        self.__rightMousePressed = False

        self.__tmFitOnFirstShow = QTimer(self)
        self.__tmFitOnFirstShow.setInterval( 100 )
        self.__tmFitOnFirstShow.setSingleShot( True )
        self.__tmFitOnFirstShow.timeout.connect( self.fitToPage )
        self.__tmFitOnFirstShow.start()

    def eventFilter(self, object, event):
        ############### Right Click Mouse Move ###############
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.RightButton:
                self.__rightMousePressed = True
                self.__moveStartX = event.x()
                self.__moveStartY = event.y()
                self.__gView.setCursor( Qt.ClosedHandCursor )
                event.accept()
                return True

        if event.type() == QEvent.MouseButtonRelease:
            if event.button() == Qt.RightButton:
                self.__rightMousePressed = False
                self.__gView.setCursor( Qt.ArrowCursor )
                event.accept()
                return True

        if event.type() == QEvent.MouseMove:
            if ( self.__rightMousePressed ):
                self.__gView.horizontalScrollBar().setValue( self.__gView.horizontalScrollBar().value() - ( event.x() - self.__moveStartX ) )
                self.__gView.verticalScrollBar().setValue  ( self.__gView.verticalScrollBar().value()   - ( event.y() - self.__moveStartY ) )
                self.__moveStartX = event.x()
                self.__moveStartY = event.y()
                event.accept()
                return True
        ############### Right Click Mouse Move ###############

        if event.type() == QEvent.KeyPress:
            if event.modifiers() & Qt.AltModifier:
                self.__gView.setDragMode( QGraphicsView.DragMode.ScrollHandDrag )
                return True

        if event.type() == QEvent.KeyRelease:
            if event.modifiers() & Qt.ControlModifier:
                if event.key() == Qt.Key_Left:
                    self.__gView.rotate( -90 )
                if event.key() == Qt.Key_Right:
                    self.__gView.rotate( 90 )
            
            if not ( event.modifiers() & Qt.AltModifier):
                self.__gView.setDragMode( QGraphicsView.DragMode.RubberBandDrag )
                return True

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


