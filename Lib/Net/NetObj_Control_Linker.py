import weakref

from PyQt5.Qt import pyqtSlot, QObject

from Lib.Common.StrConsts import SC
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV

class CNetObj_Control_Linker( QObject ):
    @property
    def netObj( self ): return self.__netObj() if self.__netObj else None

    def controlPropRef( self, control ): return control.property( self.s_propRef )

    s_propRef = "propRef"

    def __init__( self ):
        super().__init__()
        self.__netObj = None
        CNetObj_Manager.addCallback( EV.ObjPropUpdated, self.onObjPropUpdated )
        self.control_by_PropName = {}
        self.valToControlFunc_by_Control = {}
        self.valFromControlFunc_by_Control = {}

    def addControl( self, control, valToControlFunc=None, valFromControlFunc=None ):
        sPropName = self.controlPropRef( control )
        assert sPropName is not None, f'Control "{control.objectName()}" need to have custom prop "propRef" for CNetObj_Control_Linker!'
        self.control_by_PropName[ sPropName ] = control
        self.valToControlFunc_by_Control  [ control ] = valToControlFunc
        self.valFromControlFunc_by_Control[ control ] = valFromControlFunc

    def onObjPropUpdated( self, netCmd ):
        if ( self.netObj is None ) or ( netCmd.Obj_UID != self.netObj.UID ): return

        if netCmd.sPropName in self.control_by_PropName:
            control = self.control_by_PropName[ netCmd.sPropName ]
            self._updateControlState( control, netCmd.value )

    def init( self, netObj ):
        self.__netObj = weakref.ref( netObj )

        for propName, control in self.control_by_PropName.items():
            self._updateControlState( control, self.netObj[ propName ] )

    def clear( self ):
        self.__netObj = None

    def _updateControlState( self, control, value ):
        valueFunc = self.valToControlFunc_by_Control[ control ]
        value = value if valueFunc is None else valueFunc( value )
        self.updateControlState( control, value )
        
##############################################
class CNetObj_ProgressBar_Linker( CNetObj_Control_Linker ):
    def updateControlState( self, control, value ):
        control.setValue( value )

##############################################

class CNetObj_Button_Linker( CNetObj_Control_Linker ):
    def __init__( self ):
        super().__init__()
        self.trueValue_by_Btn = {}
        self.falseValue_by_Btn = {}
    
    def addButton( self, btn, trueValue, falseValue ):
        self.addControl( btn )
        self.trueValue_by_Btn[ btn ]  = trueValue
        self.falseValue_by_Btn[ btn ] = falseValue

        btn.clicked.connect( self.slotClicked )

    def updateControlState( self, control, value ):
        trueValue = self.trueValue_by_Btn[ control ]
        control.setChecked( value == trueValue )

    @pyqtSlot("bool")
    def slotClicked( self, bVal ):
        btn = self.sender()

        value  = self.trueValue_by_Btn[ btn ] if bVal else self.falseValue_by_Btn[ btn ]
        self.netObj[ self.controlPropRef( btn ) ] = value

##############################################

class CNetObj_EditLine_Linker( CNetObj_Control_Linker ):
    def addEditLine_for_Class( self, control, customClass ):
        self.addControl( control, valToControlFunc   = lambda data : data.toString(),
                                  valFromControlFunc = lambda data : customClass.fromString( data ) )
        control.returnPressed.connect( self.returnPressed )

    def addControl( self, control, valToControlFunc=None, valFromControlFunc=None ):
        super().addControl( control, valToControlFunc, valFromControlFunc )
        control.returnPressed.connect( self.returnPressed )

    def updateControlState( self, control, value ):
        control.setText( value )

    def returnPressed( self ):
        editLine = self.sender()
        propRef = self.controlPropRef( editLine )

        valueFunc = self.valFromControlFunc_by_Control[ editLine ]
        value = editLine.text()
        value = value if valueFunc is None else valueFunc( value )
        self.netObj[ propRef ] = value

        # обратное присваение нужно, т.к. если тип не принял значение из строки ( например "Idle1111" ) а в значении уже было Idle - то обновление поля не пройдет
        # и в строке ввода останется неверное значение "Idle1111"
        self._updateControlState( editLine, value )

##############################################

class CNetObj_SpinBox_Linker( CNetObj_Control_Linker ):
    def addControl( self, control, valToControlFunc=None, valFromControlFunc=None ):
        super().addControl( control, valToControlFunc, valFromControlFunc )
        control.editingFinished.connect( self.valueChanged )

    def updateControlState( self, control, value ):
        control.setValue( value )

    def valueChanged( self ):
        spinBox = self.sender()
        propRef = self.controlPropRef( spinBox )

        valueFunc = self.valFromControlFunc_by_Control[ spinBox ]
        value = spinBox.value()
        value = value if valueFunc is None else valueFunc( value )
        self.netObj[ propRef ] = value
