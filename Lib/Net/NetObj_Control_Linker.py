import weakref

from PyQt5.Qt import pyqtSlot, QObject

import Lib.Common.StrConsts as SC
from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV

class CNetObj_Control_Linker( QObject ):
    @property
    def agentNO( self ): return self.__agentNO() if self.__agentNO else None

    def controlPropRef( self, control ): return control.property( self.s_propRef )

    s_propRef = "propRef"

    def __init__( self ):
        super().__init__()
        self.__agentNO = None
        CNetObj_Manager.addCallback( EV.ObjPropUpdated, self.onObjPropUpdated )
        self.control_by_PropName = {}

    def addControl( self, control ):
        sPropName = self.controlPropRef( control )
        # sPropName = control.property( self.s_propRef )
        assert sPropName is not None, f'Control "{control.objectName()}" need to have custom prop "propRef" for CNetObj_Control_Linker!'
        self.control_by_PropName[ sPropName ] = control

    def onObjPropUpdated( self, netCmd ):
        if ( self.agentNO is None ) or ( netCmd.Obj_UID != self.agentNO.UID ): return

        if netCmd.sPropName in self.control_by_PropName:
            btn = self.control_by_PropName[ netCmd.sPropName ]
            self.updateControlState( btn, netCmd.value )

    def init( self, agentNO ):
        self.__agentNO = weakref.ref( agentNO )

        for propName, control in self.control_by_PropName.items():
            self.updateControlState( control, self.agentNO[ propName ] )

    def clear( self ):
        self.__agentNO = None
        
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
        self.agentNO[ self.controlPropRef( btn ) ] = value

##############################################

class CNetObj_EditLine_Linker( CNetObj_Control_Linker ):
    def __init__( self ):
        super().__init__()
        self.customClass_by_EditLine = {}

    def addEditLine( self, control, customClass=None ):
        self.addControl( control )
        if customClass is not None:
            self.customClass_by_EditLine[ control ] = customClass
        control.returnPressed.connect( self.returnPressed )

    def updateControlState( self, control, value ):
        control.setText( str(value) )

    def returnPressed( self ):
        editLine = self.sender()
        propRef = self.controlPropRef( editLine )
        if editLine in self.customClass_by_EditLine:
            customClass = self.customClass_by_EditLine[ editLine ]
            self.agentNO[ propRef ] = customClass.fromString( editLine.text() )

            # обратное присваение нужно, т.к. если тип не принял значение из строки ( например "Idle1111" ) а в значении уже было Idle - то обновление поля не пройдет
            # и в строке ввода останется неверное значение "Idle1111"
            editLine.setText( self.agentNO[ propRef ].name )
        else:
            self.agentNO[ propRef ] = editLine.text()

