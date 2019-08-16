import weakref

from PyQt5.Qt import pyqtSlot, QObject

from Lib.Net.NetObj_Manager import CNetObj_Manager
from Lib.Net.Net_Events import ENet_Event as EV

class CNetObj_Button_Linker( QObject ):
    @property
    def agentNO( self ): return self.__agentNO() if self.__agentNO else None

    s_propRef = "propRef"
    def __init__( self ):
        super().__init__()
        self.btn_by_PropName = {}
        self.trueValue_by_Btn = {}
        self.falseValue_by_Btn = {}
        self.__agentNO = None
        CNetObj_Manager.addCallback( EV.ObjPropUpdated, self.onObjPropUpdated )
    
    def onObjPropUpdated( self, netCmd ):
        if ( self.agentNO is None ) or ( netCmd.Obj_UID != self.agentNO.UID ): return

        if netCmd.sPropName in self.btn_by_PropName:
            btn = self.btn_by_PropName[ netCmd.sPropName ]
            self.updateBtnState( btn, netCmd.value )

    def addButton( self, btn, trueValue, falseValue ):
        sPropName = btn.property( self.s_propRef )
        assert sPropName is not None, 'Button need to have custom prop "propRef" for ButtonLinker!'
        self.btn_by_PropName[ sPropName ] = btn
        self.trueValue_by_Btn[ btn ]  = trueValue
        self.falseValue_by_Btn[ btn ] = falseValue

        btn.clicked.connect( self.slotClicked )

    def init( self, agentNO ):
        self.__agentNO = weakref.ref( agentNO )

        for propName, btn in self.btn_by_PropName.items():
            self.updateBtnState( btn, self.agentNO[ propName ] )

    def clear( self ):
        self.__agentNO = None

    def updateBtnState( self, btn, value ):
        trueValue = self.trueValue_by_Btn[ btn ]
        btn.setChecked( value == trueValue )

    @pyqtSlot("bool")
    def slotClicked( self, bVal ):
        btn = self.sender()

        value  = self.trueValue_by_Btn[ btn ] if bVal else self.falseValue_by_Btn[ btn ]
        sPropName = btn.property( self.s_propRef )
        self.agentNO[ sPropName ] = value
