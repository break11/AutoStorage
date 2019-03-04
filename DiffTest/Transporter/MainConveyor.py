# -*- coding: utf-8 -*-
import os
import sys
import struct
import termios
import fcntl
import socket
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QApplication
from serial_thread import *
import minimalmodbus
import binascii

define_MINUS_ONE_CONV_SEGMENT = 1

instrument1 = None
instrument2 = None
gModbusInitOk = 0

SERVER_IP = "192.168.0.254"
SERVER_PORT = 8889

TICKS_PER_SECOND = 50
BOX_LENGTH = 25
BOX_WIDTH = 25
BAUDRATE = 115200

AGENT_LENGTH = 50
AGENT_WIDTH = 75
AGENT_IDLE = 0
FirstStartConv = 0
GetIdString = b'\x7E\xD6\x00\x01\x00\x00\x04\x00\x00\x00\x00\xD3\x7E'
ConvMas = []
BoxMas = []

# PORT =             "/dev/serial/by-path/pci-0000:00:14.0-usb-0:11:1.0-port0"
# Weigher1PortName = "/dev/serial/by-path/pci-0000:00:14.0-usb-0:3:1.0-port0"
# Weigher2PortName = "/dev/serial/by-path/pci-0000:00:14.0-usb-0:4:1.0-port0"
# Scaner1PortName =  "/dev/serial/by-path/pci-0000:00:14.0-usb-0:10.3:1.0"#"/dev/serial/by-path/pci-0000:00:14.0-usb-0:12:1.0-port0"
# Scaner2PortName =  "/dev/serial/by-path/pci-0000:00:14.0-usb-0:10.2:1.0"
PORT =             "/dev/ttyS0"
Weigher1PortName = "/dev/ttyS1"
Weigher2PortName = "/dev/ttyS2"
Scaner1PortName =  "/dev/ttyS3"
Scaner2PortName =  "/dev/ttyS4"

TimeOutMisiion = 200
DevicesDataMas = [[Weigher1PortName, "None",TimeOutMisiion], [Weigher2PortName, "None",TimeOutMisiion], [Scaner1PortName, "None",TimeOutMisiion], [Scaner2PortName, "None",TimeOutMisiion]]

if define_MINUS_ONE_CONV_SEGMENT == 1:
    ConvMotoBlock = [[0, 1], [2], [3], [4, 5], [6], [7], [8, 9], [10], [11], [12]]
    ConvSensorBlock = [2, 3, 4, 5, 6, 7, 12, 13, 14, 16]
else:
    ConvMotoBlock = [[0], [1], [2], [3], [4, 5], [6], [7], [8, 9], [10], [11], [12]]
    ConvSensorBlock = [1, 2, 3, 4, 5, 6, 7, 12, 13, 14, 16]

TOTAL_INPUTS = 24  # 2 devices with 12 inputs each
TOTAL_OUTPUTS = 16  # 2 devices with 8 outputs each
inputs_state = [False] * TOTAL_INPUTS
outputs_state = [False] * TOTAL_OUTPUTS

define_DELAY_LOAD = 300
define_DELAY_UPLOAD = 8000
define_DELAY_BLOCKER = 135#90



'''
def do_picktest_logic():
    global gSensorEnterCurrentState
    global gSensorEnterLastState
    global gSensorExitCurrentState
    global gSensorExitLastState
    gSensorEnterCurrentState = get_input_state(SENSOR_ENTER)
    if gSensorEnterCurrentState != gSensorEnterLastState:
        if gSensorEnterCurrentState == 1:
            print("Enter sensor just lit")
            if gAgent.boxId != -1:
                gConveyorAsFifo.putBoxToFifo(gAgent.boxId)
        gSensorEnterLastState = gSensorEnterCurrentState

    gSensorExitCurrentState = get_input_state(SENSOR_EXIT)
    if gSensorExitCurrentState != gSensorExitLastState:
        if gSensorExitCurrentState == 1:
            print("Exit sensor just lit")
        gSensorExitLastState = gSensorExitCurrentState

'''
def set_conveyor_state(state):
    global conveyor_state
    conveyor_state = state

'''
def sheber_for_conveyor():
    set_output_state(SHEBER_POLE_P, 0)
    set_output_state(SHEBER_POLE_N, 1)


def sheber_for_shuttle():
    set_output_state(SHEBER_POLE_P, 1)
    set_output_state(SHEBER_POLE_N, 0)

'''
def check_mask(data, n):
    return int((data & (1 << (n))) >> (n))


def write_all_outputs_state():
    global instrument1, instrument2
    global gModbusInitOk
    i1 = 0
    i2 = 0
    if len(ConvMas) > 0:
        for Num in range(len(ConvMas)):
            if ConvMas[Num].GetTimeOutFlag() or True:
                if ConvMas[Num].motionFlag == 1:
                    for i in ConvMotoBlock[Num]:
                        outputs_state[i] = True
                else:
                    for i in ConvMotoBlock[Num]:
                        outputs_state[i] = False

    try:
        for n in range(8):
            i1 |= (outputs_state[n] << (n))
        instrument1.write_registers(50, [i1])
        for n in range(8):
            i2 |= (outputs_state[n + 8] << (n))
        instrument2.write_registers(50, [i2])
    except:
        print("ModBus CONNECTION ERROR")
        gModbusInitOk = 0


def set_output_state(output_n, state):
    outputs_state[output_n - 1] = state


def get_input_state(input_n):
    return inputs_state[input_n - 1]


def read_all_inputs_state():
    global instrument1, instrument2
    global gModbusInitOk
    try:
        i1 = instrument1.read_registers(51, 1)[0]  # returns 16-bit value, input 1 is lsb
        i2 = instrument2.read_registers(51, 1)[0]  # returns 16-bit value, input 1 is lsb
    except:
        print("ModBus CONNECTION ERROR")
        gModbusInitOk = 0

        #InitModBus()

    if gModbusInitOk == 1:
        for n in range(0, 12):
            inputs_state[n] = check_mask(i1, n)
        for n in range(0, 12):
            inputs_state[n + 12] = check_mask(i2, n)
        #print(inputs_state)
        if len(ConvMas) > 0:
            for num in range(len(ConvMas)):
                ConvMas[num].LaserStatus = inputs_state[ConvSensorBlock[num]]
                #print(ConvMas[num].LaserStatus)



def PartitionSetState(State):
    if State:
        outputs_state[14] = True
        outputs_state[15] = False
    else:
        outputs_state[14] = False
        outputs_state[15] = True

SerialAckMas = [0,0,0,0]

class ConvType:
    Weighing1 = 0
    Weighing2 = 1
    Scanning1 = 2
    Scanning2 = 3
    Operator = 4
    Loading = 5
    Unloading = 6
    NoAction = 100

class ScanerACK:
    AckScanerACK = 1
    AckScanerNACK = 2
    ReplyDeviceInfoID = 3
    ReplayData = 4
    WaitData = 5

class WeigherACK:
    NoACK = 0
    ReplayTareReset = 1
    ReplayTareInput = 2
    WaitData = 3

class MissionLevel:
    Wait = 0
    Complit = 1
    Ready = 2

class MainWindow(QtWidgets.QMainWindow):

    writeDataToWeighterSignal = QtCore.pyqtSignal(str)
    writeDataToScannerSignal = QtCore.pyqtSignal(str)

    def __init__(self):
        super(MainWindow, self).__init__()
        global global_mainWindow
        global_mainWindow = self
        self.CanStart = False
        self.FirstStart = 0
        self.count = 0
        self.timerEventCounter = 0
        self.NewBoxTimeOut = define_DELAY_LOAD
        self._change_timer = QTimer()
        self._change_timer.setInterval(1500)
        self._change_timer.setSingleShot(True)
        self._change_timer.timeout.connect(self.StatrtInitPerefFunc)
        self._change_timer.start()

        self._conv_timer = QTimer()
        self._conv_timer.setInterval(50)
        self._conv_timer.setSingleShot(False)
        #self._conv_timer.timeout.connect(self.ConvTimerTick)
        self._conv_timer.start()


        self._conv_timer2 = QTimer()
        self._conv_timer2.setInterval(50)
        self._conv_timer2.setSingleShot(False)
        self._conv_timer2.timeout.connect(self.ConvTimerMove)
        self._conv_timer2.start()


        self._temp_timer = QTimer()
        self._temp_timer.setInterval(2000)
        self._temp_timer.setSingleShot(False)
        self._temp_timer.timeout.connect(self.TimerTick)
        self._temp_timer.start()

        self.ConvBoxDelTimer = QTimer()
        self.ConvBoxDelTimer.setInterval(define_DELAY_UPLOAD)
        self.ConvBoxDelTimer.setSingleShot(True)
        self.ConvBoxDelTimer.timeout.connect(self.ConvBoxDel)
        #self.ConvBoxDelTimer.start()

        self.ModBusReconnectTimer = QTimer()
        self.ModBusReconnectTimer.setInterval(500)
        self.ModBusReconnectTimer.setSingleShot(False)
        self.ModBusReconnectTimer.timeout.connect(self.InitModBus)
        self.ModBusReconnectTimer.start()


        self.menuLayout_Connections = QtWidgets.QGridLayout()
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.setSceneRect(0, -50, 1200, 800)

        pen = QtGui.QPen(QtCore.Qt.blue)
        side = 100
        gap = 5
        ConvMas.append(ConveyorAsFifo((side + gap) * 1, side, ConvType.Scanning1, "Scanning1"))
        if define_MINUS_ONE_CONV_SEGMENT == 0:
            ConvMas.append(ConveyorAsFifo((side + gap) * 2, side, ConvType.NoAction, "None"))
        ConvMas.append(ConveyorAsFifo((side + gap) * 3, side, ConvType.NoAction, "None"))
        ConvMas.append(ConveyorAsFifo((side + gap) * 4, side, ConvType.Weighing1, "Weighing1"))
        ConvMas.append(ConveyorAsFifo((side + gap) * 5, side, ConvType.NoAction, "None"))
        ConvMas.append(ConveyorAsFifo((side + gap) * 6, side, ConvType.NoAction, "Pick"))
        ConvMas.append(ConveyorAsFifo((side + gap) * 7, side, ConvType.NoAction, "None"))
        ConvMas.append(ConveyorAsFifo((side + gap) * 8, side, ConvType.Weighing2, "Weighing2"))
        ConvMas.append(ConveyorAsFifo((side + gap) * 9, side, ConvType.NoAction, "None"))
        ConvMas.append(ConveyorAsFifo((side + gap) * 10, side, ConvType.NoAction, "None"))
        ConvMas.append(ConveyorAsFifo((side + gap) * 11, side, ConvType.Scanning2, "Scanning2"))

        for i in range(len(ConvMas)):
            self.scene.addItem(ConvMas[i])
        #for i in range(7):
            #self.scene.addItem(ConveyorAsFifo(10, 10))
            #ConvMas.append(ConveyorAsFifo(25+210*i, 200, ConvType.Loading, "Block №: " + str(i)))
        #    self.scene.addItem(ConvMas[i])
        #ConvMas[0].ConveyorType = ConvType.Loading

        #box0 = Box(0, "BOX" + str(len(BoxMas)))
        #box1 = Box(0, "BOX" + str(len(BoxMas)))
        #box1 = Box(1, "BOX" + str(len(BoxMas)))
        '''
        BoxMas.append(box0)

        for i in BoxMas:
            self.scene.addItem(i)

        ConvMas[0].AddBox(box0)
        '''

        '''
        for i in range(7):
            ConvMas.append(Conveyor(QtCore.QRectF(QtCore.QPointF(i*side, side), QtCore.QSizeF(195, 250)),0,1))
            self.scene.addRect(ConvMas[i].Size, pen)
            #self.scene.tex
            if(ConvMas[i].StartLaser == 1):
                self.scene.addLine(side * i + 30, side - 50, side * i + 30, side + 250 + 50)
            if (ConvMas[i].StopLaser == 1):
                self.scene.addLine(side + side * i - 30, side - 50, side + side * i - 30, side + 250 + 50)
        '''
        #self.scene.addRect(r, pen)
        self.view = QtWidgets.QGraphicsView(self.scene)

        self.textEdit = QtWidgets.QTextEdit()
        self.textEdit.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.leftPanel = QtWidgets.QTabWidget()
        self.leftPanel.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Ignored))

        self.ScanSerialButton = QtWidgets.QPushButton(u"Найти активные порты")
        self.ScanSerialButton.clicked.connect(self.ScanSerialButtonClicked)
        self.ScanSerialButton.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Times))
        self.ScanSerialButton.setMinimumSize(0, 50)
        self.menuLayout_Connections.addWidget(self.ScanSerialButton, 0, 0, 1, 1)


        self.Button1 = QtWidgets.QPushButton(u"Button1")
        self.Button1.clicked.connect(self.Button1Clicked)
        self.Button1.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Times))
        self.Button1.setMinimumSize(0, 50)
        self.menuLayout_Connections.addWidget(self.Button1, 1, 0, 1, 1)

        self.Button2 = QtWidgets.QPushButton(u"Button2")
        self.Button2.clicked.connect(self.Button2Clicked)
        self.Button2.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Times))
        self.Button2.setMinimumSize(0, 50)
        self.menuLayout_Connections.addWidget(self.Button2, 2, 0, 1, 1)

        self.Button3 = QtWidgets.QPushButton(u"Button3")
        self.Button3.clicked.connect(self.Button3Clicked)
        self.Button3.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Times))
        self.Button3.setMinimumSize(0, 50)
        self.menuLayout_Connections.addWidget(self.Button3, 3, 0, 1, 1)

        self.Button4 = QtWidgets.QPushButton(u"Button4")
        self.Button4.clicked.connect(self.Button4Clicked)
        self.Button4.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Times))
        self.Button4.setMinimumSize(0, 50)
        self.menuLayout_Connections.addWidget(self.Button4, 4, 0, 1, 1)

        self.Button5 = QtWidgets.QPushButton(u"Button5")
        self.Button5.clicked.connect(self.Button5Clicked)
        self.Button5.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Times))
        self.Button5.setMinimumSize(0, 50)
        self.menuLayout_Connections.addWidget(self.Button5, 5, 0, 1, 1)

        self.Button6 = QtWidgets.QPushButton(u"Button6")
        self.Button6.clicked.connect(self.Button6Clicked)
        self.Button6.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Times))
        self.Button6.setMinimumSize(0, 50)
        self.menuLayout_Connections.addWidget(self.Button6, 6, 0, 1, 1)

        self.Button7 = QtWidgets.QPushButton(u"Button7")
        self.Button7.clicked.connect(self.Button7Clicked)
        self.Button7.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Times))
        self.Button7.setMinimumSize(0, 50)
        self.menuLayout_Connections.addWidget(self.Button7, 7, 0, 1, 1)

        self.Button8 = QtWidgets.QPushButton(u"Button8")
        self.Button8.clicked.connect(self.Button8Clicked)
        self.Button8.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Times))
        self.Button8.setMinimumSize(0, 50)
        self.menuLayout_Connections.addWidget(self.Button8, 8, 0, 1, 1)

        self.Button9 = QtWidgets.QPushButton(u"Button9")
        self.Button9.clicked.connect(self.Button9Clicked)
        self.Button9.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Times))
        self.Button9.setMinimumSize(0, 50)
        self.menuLayout_Connections.addWidget(self.Button9, 9, 0, 1, 1)

        self.Button10 = QtWidgets.QPushButton(u"Button10")
        self.Button10.clicked.connect(self.Button10Clicked)
        self.Button10.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Times))
        self.Button10.setMinimumSize(0, 50)
        self.menuLayout_Connections.addWidget(self.Button10, 10, 0, 1, 1)




        self.LabelWeigher1 = QtWidgets.QLabel(u"DATA1")
        self.LabelWeigher1.setFont(QtGui.QFont("Times", 11, QtGui.QFont.Bold))
        self.menuLayout_Connections.addWidget(self.LabelWeigher1, 11, 0, 1, 1)

        self.LabelScan1 = QtWidgets.QLabel(u"DATA2")
        self.LabelScan1.setFont(QtGui.QFont("Times", 11, QtGui.QFont.Bold))
        self.menuLayout_Connections.addWidget(self.LabelScan1, 12, 0, 1, 1, alignment=QtCore.Qt.AlignTop)

        self.LabelWeigher2 = QtWidgets.QLabel(u"DATA3")
        self.LabelWeigher2.setFont(QtGui.QFont("Times", 11, QtGui.QFont.Bold))
        self.menuLayout_Connections.addWidget(self.LabelWeigher2, 13, 0, 1, 1)

        self.LabelScan2 = QtWidgets.QLabel(u"DATA4")
        self.LabelScan2.setFont(QtGui.QFont("Times", 11, QtGui.QFont.Bold))
        self.menuLayout_Connections.addWidget(self.LabelScan2, 14, 0, 1, 1, alignment=QtCore.Qt.AlignTop)

        self.serverConnectionStatusLabel = QtWidgets.QLabel(u"SERVER")
        self.serverConnectionStatusLabel.setFont(QtGui.QFont("Times", 11, QtGui.QFont.Bold))
        self.menuLayout_Connections.addWidget(self.serverConnectionStatusLabel, 15, 0, 1, 1)

        self.ErrorLabel = QtWidgets.QLabel(u"ERROR")
        self.ErrorLabel.setFont(QtGui.QFont("Times", 11, QtGui.QFont.Bold))
        self.menuLayout_Connections.addWidget(self.ErrorLabel, 16, 0, 1, 1)

        self.menuWidget_Calibration = QtWidgets.QWidget()
        self.menuWidget_Calibration.setLayout(self.menuLayout_Connections)

        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addWidget(self.menuWidget_Calibration)
        mainLayout.addWidget(self.view)#(self.textEdit)
        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(mainLayout)
        self.setCentralWidget(self.widget)
        self.setWindowTitle("Конвейер")

        self.serialPortWeigher1 = WorkerThread(Weigher1PortName, 9600, None)
        self.serialPortWeigher1.start()
        self.serialPortWeigher1.dataReady.connect(self.ParsingWeigher1)

        self.serialPortScan1 = WorkerThread(Scaner1PortName, 9600, "~")
        self.serialPortScan1.start()
        self.serialPortScan1.dataReady.connect(self.ParsingScan1)

        self.serialPortWeigher2 = WorkerThread(Weigher2PortName, 9600, None)
        self.serialPortWeigher2.start()
        self.serialPortWeigher2.dataReady.connect(self.ParsingWeigher2)

        self.serialPortScan2 = WorkerThread(Scaner2PortName, 9600, "~")
        self.serialPortScan2.start()
        self.serialPortScan2.dataReady.connect(self.ParsingScan2)

        self.CanStart = True
        #self.writeDataToWeighterSignal.connect(self.serialPortWeigher1.WriteDataToPortDirectly)

        #self.writeDataToWeighterSignal.emit("BBB")
        self.scene.update()
        self.view.update()
        self.timerId = self.startTimer(1000 / TICKS_PER_SECOND)
        #InitModBus()
        strtmp = "7e0f00000000000f7e3030303030303030303135340d"
        tempstr = ""
        print(strtmp)
        if strtmp.find("7e0f00000000000f7e") != -1:
                if len(strtmp) > len("7e0f00000000000f7e"):
                    tempstr = strtmp.replace("7e0f00000000000f7e","")
                    b = bytes.fromhex(tempstr)
                    tempstr = b.decode("utf-8")
                    #tempstr = binascii.hexlify(tempstr)
                    print(tempstr)
                    #tempstr = tempstr.decode("cp1254").encode("utf-8")

    def ConvTimerMove(self):
        global gModbusInitOk
        if gModbusInitOk:
            #self.FirstStartFunc()
            read_all_inputs_state()
            write_all_outputs_state()
        if len(ConvMas) > 0:
            #print(ConvMas[len(ConvMas)-1].MissionForTypeDone)
            self.ConvBoxLoadLogic()

            for Num in range(len(ConvMas)):
                ConvMas[Num].MissionTimeoutDec()
                if Num == len(ConvMas):
                    NextNum = -1
                else:
                    NextNum = Num + 1


                if len(ConvMas[Num].BoxList) > 0:

                        if ConvMas[Num].LaserStatus == 1:
                            if Num == len(ConvMas)-1:
                                PartitionSetState(False)
                            if ConvMas[Num].BoxList[0].biasX < 50:
                                ConvMas[Num].BoxList[0].MoveBox(50, 0)
                                ConvMas[Num].PrintBox(ConvMas[Num].BoxList[0])

                            if ConvMas[Num].GetMissionForTypeDone() == MissionLevel.Complit:
                                if Num != len(ConvMas)-1:
                                    if len(ConvMas[NextNum].BoxList) == 0 and ConvMas[NextNum].GetMissionTimeout() == 0:
                                        #ConvMas[Num + 1].MissionForTypeDone = 0
                                        ConvMas[Num].SetMotion(1)
                                        ConvMas[NextNum].SetMotion(1)
                                    else:
                                        ConvMas[Num].SetMotion(0)
                                else:
                                    ConvMas[Num].SetMotion(0)
                            else:
                                ConvMas[Num].SetMotion(0)
                                status = self.CheckConvMissionForType(ConvMas[Num].ConveyorType)
                                if status != "WAIT" and status != "None":
                                    print(str(Num) +" MISSION COMPLIT ==================================================")
                                    print(DevicesDataMas)
                                    ConvMas[Num].MissionForTypeDone = MissionLevel.Complit
                                    self.updateBoxParameters(ConvMas[Num].ConveyorType, ConvMas[Num].BoxList[0], status)
                                else:
                                    #if ConvMas[Num].ConveyorType != ConvType.NoAction:
                                    if ConvMas[Num].ConveyorType == ConvType.Weighing1 or ConvMas[Num].ConveyorType == ConvType.Weighing2:
                                        if self.CheckConvMissionForType(ConvMas[Num].ConveyorType) == "None":
                                            self.StartConvMission(ConvMas[Num].ConveyorType)
                        else:
                            if ConvMas[Num].PreLaserStatus == 1:
                                if Num < len(ConvMas)-1:
                                    ConvMas[Num].BoxList[0].BoxReset()
                                    ConvMas[NextNum].AddBox(ConvMas[Num].BoxList[0])
                                    ConvMas[Num].RemoveBox()
                                    ConvMas[NextNum].PrintBox(ConvMas[NextNum].BoxList[0])
                                    ConvMas[Num].SetMotion(0)
                                else:

                                    #ConvMas[Num].BoxList[0].BoxReset()

                                    ConvMas[len(ConvMas)-1].SetMotion(0)
                                    self.ConvBoxDelTimerFunc()


                                #print("/////")
                                #print(ConvMas[Num+1].BoxList)
                                #print(len(ConvMas[Num].BoxList))
                                #print(len(ConvMas[Num+1].BoxList))

                            else:
                                if ConvMas[Num].GetMissionForTypeDone() != MissionLevel.Complit:
                                    status = self.CheckConvMissionForType(ConvMas[Num].ConveyorType)
                                    if status != "WAIT" and status != "None":
                                        print(str(Num) +" MISSION COMPLIT ==================================================")
                                        print(DevicesDataMas)
                                        ConvMas[Num].MissionForTypeDone = MissionLevel.Complit
                                        self.updateBoxParameters(ConvMas[Num].ConveyorType, ConvMas[Num].BoxList[0], status)
                                    else:
                                        if ConvMas[Num].ConveyorType == ConvType.Scanning1 or ConvMas[Num].ConveyorType == ConvType.Scanning2:
                                            if self.CheckConvMissionForType(ConvMas[Num].ConveyorType) == "None":
                                                self.StartConvMission(ConvMas[Num].ConveyorType)
                                ConvMas[Num].SetMotion(1)
                        ConvMas[Num].PreLaserStatus = ConvMas[Num].LaserStatus


    def timerEvent(self, event):

        if gServerConnection.IsConnected():
            gServerConnection.receive()

        self.timerEventCounter += 1
        if self.timerEventCounter == TICKS_PER_SECOND:
            self.timerEventCounter = 0
            # each second event
            # print "One second passed"
            if gServerConnection.IsConnected():
                self.serverConnectionStatusLabel.setText(u"Server: CONNECTED")
                self.serverConnectionStatusLabel.setStyleSheet("QLabel { color : green; }");
            else:
                self.serverConnectionStatusLabel.setText(u"Server: DISCONNECTED")
                self.serverConnectionStatusLabel.setStyleSheet("QLabel { color : red; }");
            # print ("gServerConnection.IsConnected()=%d" % gServerConnection.IsConnected())
            # print ("gServerConnection.GetPings()=%d" % gServerConnection.GetPings())

            gServerConnection.DecreasePing()
            if gServerConnection.GetPings() == 0:
                gServerConnection.reconnect()



    def ConvBoxDelTimerFunc(self):
            ConvMas[len(ConvMas)-1].SetMissionTimeout(define_DELAY_BLOCKER)
            ConvMas[len(ConvMas)-1].RemoveBox()
            self.ConvBoxDelTimer.start()
    def ConvBoxDel(self):
            PartitionSetState(True)
            ConvMas[len(ConvMas)-1].SetMotion(0)
            write_all_outputs_state()
            self.scene.removeItem(BoxMas[0])
            #ConvMas[len(ConvMas)-1].RemoveBox()
            BoxMas.pop(0)
            ConvMas[len(ConvMas)-1].ResetConvStatus()
    def ConvBoxLoadLogic(self):
        if self.CanStart == True:
            if self.NewBoxTimeOut > 0 and inputs_state[0] == 1:
                self.NewBoxTimeOut -= 1
            else:
                self.NewBoxTimeOut = define_DELAY_LOAD
            if inputs_state[0] == 1 and  len(ConvMas[0].BoxList) == 0 and self.NewBoxTimeOut == 0:
                #self.NewBoxTimeOut = 200
                BoxMas.append(Box(0, "BOX" + str(len(BoxMas))))
                self.scene.addItem(BoxMas[len(BoxMas) - 1])
                ConvMas[0].AddBox(BoxMas[len(BoxMas) - 1])

    def FirstStartFunc(self):
        print("FirstStartFunc()")
        PartitionSetState(True)
        for num in range(len(ConvMas)):
            if ConvMas[len(ConvMas)-1 -num].LaserStatus == 1:
                BoxMas.append(Box(0, "BOX" + str(len(BoxMas))))
                self.scene.addItem(BoxMas[len(BoxMas) - 1])
                ConvMas[len(ConvMas)-1 -num].AddBox(BoxMas[len(BoxMas) - 1])
                if num == 0:
                    ConvMas[-1].MissionForTypeDone = MissionLevel.Complit
                    PartitionSetState(False)
        print(str(len(ConvMas))+"And Box: "+str(len(BoxMas)))


    def InitModBus(self):
        global instrument1, instrument2
        global gModbusInitOk
        if gModbusInitOk == 0:
            minimalmodbus.BAUDRATE = BAUDRATE
            #try:
            instrument1 = minimalmodbus.Instrument(PORT, 1, minimalmodbus.MODE_ASCII)
            instrument2 = minimalmodbus.Instrument(PORT, 2, minimalmodbus.MODE_ASCII)
            fd = os.open(PORT, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
            fcntl.ioctl(fd, termios.TIOCMBIC, struct.pack('I', termios.TIOCM_DTR))
            iflag, oflag, cflag, lflag, ispeed, ospeed, cc = termios.tcgetattr(fd)
            cflag &= ~(termios.CRTSCTS)
            termios.tcsetattr(fd, termios.TCSANOW, [iflag, oflag, cflag, lflag, ispeed, ospeed, cc])
            gModbusInitOk = 1
            print("ModBusInit: OK")
            #except:
            #   print ("No modbus devices found!")
            #  gModbusInitOk = 0
            #gFakeConveyor = 1

    def TimerTick(self):
        self.count = 200
        #if self.count == 5:
            #ConvMas[2].SetLaserStatus(0)
        if self.count == 0:
            #ConvMas[0].MissionForTypeDone = 1
            ConvMas[0].SetLaserStatus(1)

        if self.count == 1:
            ConvMas[0].SetLaserStatus(0)

        if self.count == 2:
            #ConvMas[1].MissionForTypeDone = 1
            ConvMas[1].SetLaserStatus(1)

        if self.count == 3:
            ConvMas[1].SetLaserStatus(0)

        if self.count == 4:
            #ConvMas[2].MissionForTypeDone = 1
            ConvMas[2].SetLaserStatus(1)

        if self.count == 5:
            ConvMas[2].SetLaserStatus(0)

        if self.count == 6:
            #ConvMas[3].MissionForTypeDone = 1
            ConvMas[3].SetLaserStatus(1)

        if self.count == 7:
            ConvMas[3].SetLaserStatus(0)

        self.count += 1
        if self.count >= 8:
            self.count = 0




    def GetTextEditEndPos(self):
        return int(self.TextEditEndPos.text())

    def GetTextEditStartPos(self):
        return int(self.TextEditStartPos.text())

    def onUpdateText(self, text):
        cursor = self.textEdit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.textEdit.setTextCursor(cursor)
        self.textEdit.ensureCursorVisible()

    def __del__(self):
        self.serialPortWeigher1.exit()
        sys.stdout = sys.__stdout__

    def center(self):
        # geometry of the main window
        qr = self.frameGeometry()
        # center point of screen
        cp = QDesktopWidget().availableGeometry().center()
        # move rectangle's center point to screen's center point
        qr.moveCenter(cp)
        # top left of rectangle becomes top left of window centering it
        self.move(qr.topLeft())

    def ScanSerialButtonClicked(self):
        print("123")


    def ParsingScan1(self, portName, message):
        global SerialAckMas
        data = message.encode("latin-1").hex()
        print(data)
        txt = "S1 :" + portName + " ACK: " + data
        #txt = CreateCommandForScaner("d60001", "00", "0004", "00000000")#b'\x7E\xD6\x00\x01\x00\x00\x04\x00\x00\x00\x00\xD3\x7E'
        #print(message)
        print(txt)
        #self.LabelWeigher1.setText(txt)
        if SerialAckMas[2] == ScanerACK.AckScanerACK:
            print(SerialAckMas)
            SerialAckMas[2] = 0

            if (data == "7e0f00000000000f7e"):
                #ResetWriteFlag(self.serialPortScan1)
                print("ACK: AckScanerACK")
            if (data == "7e0e000d000000037e"):
                #ResetWriteFlag(self.serialPortScan1)
                self.serialPortScan1.LastPacketError = 1
                print("ACK: AckScanerNACK")

        if SerialAckMas[2] == ScanerACK.WaitData:
            print(SerialAckMas)
            SerialAckMas[2] = 0
            self.LabelScan1.setText(message)
            print("Barcode: " + message)
            for i in range(len(DevicesDataMas)):
                if DevicesDataMas[i][0] == portName:
                    DevicesDataMas[i][1] = message
                    print("=============")
                    #print(DevicesDataMas)
                    #SendSerialPortData(self.serialPortScan1, CreateCommandForScaner("800200", "00", "00"),ScanerACK.AckScanerACK)

        if SerialAckMas[2] == ScanerACK.ReplayData:
            print(SerialAckMas)
            SerialAckMas[2] = 0
            print("ACK: ScanerACK.ReplayData")
            if data.find("7e0f00000000000f7e") != -1:
                if len(data) > len("7e0f00000000000f7e"):
                    tempstr = data.replace("7e0f00000000000f7e","")
                    b = bytes.fromhex(tempstr)
                    tempstr = b.decode("latin-1")
                    SerialAckMas[2] = 0
                    self.LabelScan1.setText(tempstr)
                    print("Barcode: " + tempstr)
                    for i in range(len(DevicesDataMas)):
                        if DevicesDataMas[i][0] == portName:
                            DevicesDataMas[i][1] = tempstr
                            #print("===============================================================")
                            #print(DevicesDataMas)
                else:
                    #ResetWriteFlag(self.serialPortScan1)
                    SerialAckMas[2] = ScanerACK.WaitData
                    print("ACK: ScanerACK.WaitData")
            if (data == "7e0e000d000000037e"):
                SerialAckMas[2] = 0
                self.serialPortScan1.LastPacketError = 1
                print("ACK: Device NACK ERROR")

        if SerialAckMas[2] == ScanerACK.ReplyDeviceInfoID:
            SerialAckMas[2] = 0
            if(data[0:2] == "7e"):
                print("ACK: ReplyDeviceInfoID: " + data[14:14+int(data[10:14])*2])

    def ParsingScan2(self, portName, message):
        data = message.encode("latin-1").hex()
        txt = "S2 :" + portName + " ACK: " + data
        #txt = CreateCommandForScaner("d60001", "00", "0004", "00000000")#b'\x7E\xD6\x00\x01\x00\x00\x04\x00\x00\x00\x00\xD3\x7E'
        #print(message)
        print(txt)
        #self.LabelWeigher1.setText(txt)

        if SerialAckMas[3] == ScanerACK.AckScanerACK:
            if (data == "7e0f00000000000f7e"):
                SerialAckMas[3] = 0
                print("ACK: AckScanerACK")
            if (data == "7e0e000d000000037e"):
                SerialAckMas[3] = 0
                self.serialPortScan2.LastPacketError = 1
                print("ACK: AckScanerNACK")

        if SerialAckMas[3] == ScanerACK.WaitData:
            SerialAckMas[3] = 0
            self.LabelScan2.setText(message)
            print("Barcode: " + message)
            for i in range(len(DevicesDataMas)):
                if DevicesDataMas[i][0] == portName:

                    DevicesDataMas[i][1] = message
                    #print("===============================================================")
                    #print(DevicesDataMas)
                    #SendSerialPortData(self.serialPortScan1, CreateCommandForScaner("800200", "00", "00"),ScanerACK.AckScanerACK)

        if SerialAckMas[3] == ScanerACK.ReplayData:
            SerialAckMas[3] = 0
            print("ACK: ScanerACK.ReplayData")
            if data.find("7e0f00000000000f7e") != -1:
                if len(data) > len("7e0f00000000000f7e"):
                    tempstr = data.replace("7e0f00000000000f7e","")
                    b = bytes.fromhex(tempstr)
                    tempstr = b.decode("latin-1")
                    SerialAckMas[3] = 0
                    self.LabelScan2.setText(tempstr)
                    print("Barcode: " + tempstr)
                    for i in range(len(DevicesDataMas)):
                        if DevicesDataMas[i][0] == portName:
                            DevicesDataMas[i][1] = tempstr
                            #print("===============================================================")
                            #print(DevicesDataMas)
                else:
                    SerialAckMas[3] = 0
                    SerialAckMas[3] = ScanerACK.WaitData
                    print("ACK: ScanerACK.WaitData")
            if (data == "7e0e000d000000037e"):
                SerialAckMas[3] = 0
                self.serialPortScan2.LastPacketError = 1
                print("ACK: Device NACK ERROR")

        if SerialAckMas[3] == ScanerACK.ReplyDeviceInfoID:
            SerialAckMas[3] = 0
            if(data[0:2] == "7e"):
                print("ACK: ReplyDeviceInfoID: " + data[14:14+int(data[10:14])*2])

    def ParsingWeigher1(self, portName, message):
        global SerialAckMas
        #print(portName + ": " + message)
        #txt = "W1" + portName + ": " + message

        data = message.encode("latin-1").hex()
        txt = "W1" + portName + " ACK: " + message + " / " + data
        #txt = CreateCommandForScaner("d60001", "00", "0004", "00000000")#b'\x7E\xD6\x00\x01\x00\x00\x04\x00\x00\x00\x00\xD3\x7E'
        #print(txt)
        #self.LabelWeigher1.setText(txt)
        #print("W1" + message + " : " + str(self.serialPortWeigher1.WaitACK))
        if SerialAckMas[0] == WeigherACK.WaitData:
            print(SerialAckMas)
            SerialAckMas[0] = 0
            #self.serialPortScan1.WaitData = 0

            print("W1 ACK=" + " : " +message)
            if message.count("ST,NT,+"):
                #print(message)
                self.LabelWeigher1.setText(message)
                for i in range(len(DevicesDataMas)):
                    if DevicesDataMas[i][0] == portName:
                        WeightFloatStr = message.replace("ST,NT,+", "")
                        WeightFloatStr = WeightFloatStr.replace("kg\r\n", "")
                        DevicesDataMas[i][1] = float(WeightFloatStr)
                        #print("=============")
                        #print(DevicesDataMas)

            else:
                print("W1 wait stable status")
                SerialAckMas[0] = WeigherACK.WaitData



        if SerialAckMas[0] == WeigherACK.ReplayTareInput:
            #self.LabelWeigher1.setText(txt)
            #print(data)
            if data.count("023031575441520603"):
                print("ACK: WeigherACK.ReplayTareInput")
                SerialAckMas[0] = 0
        if SerialAckMas[0] == WeigherACK.ReplayTareReset:
            #self.LabelWeigher1.setText(txt)
            #print(data)
            if data.count("023031575452530603"):
                print("ACK: WeigherACK.ReplayTareReset")
                SerialAckMas[0] = 0

    def ParsingWeigher2(self, portName, message):
        global SerialAckMas
        #print(portName + ": " + message)
        #txt = "W1" + portName + ": " + message

        data = message.encode("latin-1").hex()
        txt = "W1" + portName + " ACK: " + message + " / " + data
        #txt = CreateCommandForScaner("d60001", "00", "0004", "00000000")#b'\x7E\xD6\x00\x01\x00\x00\x04\x00\x00\x00\x00\xD3\x7E'
        #print(txt)
        #self.LabelWeigher1.setText(txt)

        if SerialAckMas[1] == WeigherACK.WaitData:
            print(SerialAckMas)
            SerialAckMas[1] = 0
            #self.serialPortScan1.WaitData = 0
            print("W2 ACK=" + " : " +message)
            #print(message)
            if message.count("ST,NT,+"):
                #print(message)
                self.LabelWeigher2.setText(message)
                for i in range(len(DevicesDataMas)):
                    if DevicesDataMas[i][0] == portName:
                        WeightFloatStr = message.replace("ST,NT,+", "")
                        WeightFloatStr = WeightFloatStr.replace("kg\r\n", "")
                        DevicesDataMas[i][1] = float(WeightFloatStr)
                        #print("=============")
                        #print(DevicesDataMas)

            else:
                print("W2 wait stable status")
                SerialAckMas[1] = WeigherACK.WaitData



        if SerialAckMas[1] == WeigherACK.ReplayTareInput:
            #self.LabelWeigher1.setText(txt)
            #print(data)
            if data.count("023031575441520603"):
                print("ACK: WeigherACK.ReplayTareInput")
                SerialAckMas[1] = 0
        if SerialAckMas[1] == WeigherACK.ReplayTareReset:
            #self.LabelWeigher1.setText(txt)
            #print(data)
            if data.count("023031575452530603"):
                print("ACK: WeigherACK.ReplayTareReset")
                SerialAckMas[1] = 0

    def aaa(self):
        self.writeDataToWeighterSignal.emit("BBB")

    @pyqtSlot()
    def StatrtInitPerefFunc(self):
        print("INIT")
        self.FirstStartFunc()
        #self.aaa()
        #self.writeDataToWeighterSignal.emit("BBB")
        #self.serialPortWeigher1.SendData()
        #self.serialPortWeigher1.SendData(b'\x02\x30\x31\x57\x54\x41\x52\x03')

        #self.serialPortWeigher1.WriteQueue.put(b'\x02\x30\x31\x57\x54\x41\x52\x06\x03')
        #self.serialPortWeigher1.WaitACK = WeigherACK.NoACK

        #SendSerialPortData(self.serialPortWeigher1, b'\x02\x30\x31\x57\x48\x4f\x4c\x03', WeigherACK.ReplayTareReset)
        #sleep(1.0)
        #SendSerialPortData(self.serialPortWeigher1, b'\x02\x30\x31\x57\x54\x52\x53\x03', WeigherACK.ReplayTareReset)
        #sleep(1.0)
        #SendSerialPortData(self.serialPortWeigher1, b'\x02\x30\x31\x57\x54\x41\x52\x03', WeigherACK.ReplayTareInput)

        #SendSerialPortData(self.serialPortScan1, CreateCommandForScaner("d60001", "00", "00000000"), ScanerACK.ReplyDeviceInfoID)
        #SendSerialPortData(self.serialPortScan2, CreateCommandForScaner("800200", "00", "01"), ScanerACK.ReplayData)
        #SetWriteFlag(self.serialPortScan1, ScanerACK.WaitData)
        #SetWriteFlag(self.serialPortWeigher1, WeigherACK.WaitData)

    def updateBoxParameters(self, device, Box, data):
        if device == 2:
            Box.ID_Number = data
        if device == 3:
            if Box.ID_Number != data and Box.ID_Number != 0:
                print("ERROR Box.ID_Number = " + Box.ID_Number)
                self.ErrorLabel.setText(u"S2 ERROR")
                self.ErrorLabel.setStyleSheet("QLabel { color : red; }");
        if device == 0:
            Box.weight = data
        if device ==1:
            Box.deltaWeight =  data - Box.weight
        #print(data)

    def CheckConvMissionForType(self, device):

        if device != ConvType.NoAction:
            #print("------------------------------------------------------------------")
            #print(device, DevicesDataMas[device][1], DevicesDataMas[device][2])
            #print("------------------------------------------------------------------")
            Status = DevicesDataMas[device][1]
            TimeOut = DevicesDataMas[device][2]
            if DevicesDataMas[device][2] == 0 and DevicesDataMas[device][1] == "WAIT":
                print(str(device)+" TIMEOUT-----------------------------------------------------------------------")

                DevicesDataMas[device][1] = "None"
            else:
                DevicesDataMas[device][2] -= 1

            if DevicesDataMas[device][1] != "WAIT":
                DevicesDataMas[device][1] = "None"
            return Status
        else:
            return "OK"

    def StartConvMission(self, device):
        global TimeOutMisiion
        DevicesDataMas[device][2] = TimeOutMisiion
        print(str(device)+" SEND COMMAND serial ")
        if device == ConvType.Weighing1:
            if DevicesDataMas[device][1] != "WAIT":
                DevicesDataMas[device][1] = "WAIT"
                SerialAckMas[0] = WeigherACK.WaitData
        if device == ConvType.Weighing2:
            if DevicesDataMas[device][1] != "WAIT":
                DevicesDataMas[device][1] = "WAIT"
                SerialAckMas[1] = WeigherACK.WaitData
        if device == ConvType.Scanning1:
            if DevicesDataMas[device][1] != "WAIT":
                temp = "DevicesDataMas[device][1]" + DevicesDataMas[device][1]
                print(temp)
                DevicesDataMas[device][1] = "WAIT"
                SerialAckMas[2] = ScanerACK.ReplayData
                SendSerialPortData(self.serialPortScan1, CreateCommandForScaner("800200", "00", "01"))
        if device == ConvType.Scanning2:
            if DevicesDataMas[device][1] != "WAIT":
                PartitionSetState(False)
                temp = "DevicesDataMas[device][1]" + DevicesDataMas[device][1]
                print(temp)
                DevicesDataMas[device][1] = "WAIT"
                SerialAckMas[3] = ScanerACK.ReplayData
                SendSerialPortData(self.serialPortScan2, CreateCommandForScaner("800200", "00", "01"))



    def Button1Clicked(self):
        print("Button1Clicked")
        #ConvMas[0].MissionForTypeDone = 1
        #ConvMas[0].SetLaserStatus(1)
        BoxMas.append(Box(0, "BOX" + str(len(BoxMas))))
        self.scene.addItem(BoxMas[len(BoxMas)-1])
        ConvMas[0].AddBox(BoxMas[len(BoxMas)-1])
    def Button2Clicked(self):
        print("Button2Clicked")
        ConvMas[0].SetLaserStatus(1)
    def Button3Clicked(self):
        print("Button3Clicked")
        ConvMas[0].SetLaserStatus(0)
    def Button4Clicked(self):
        print("Button4Clicked")
        ConvMas[1].SetLaserStatus(1)
    def Button5Clicked(self):
        print("Button5Clicked")
        ConvMas[1].SetLaserStatus(0)
    def Button6Clicked(self):
        print("Button6Clicked")
        ConvMas[2].SetLaserStatus(1)
    def Button7Clicked(self):
        print("Button7Clicked")
        ConvMas[2].SetLaserStatus(0)
    def Button8Clicked(self):
        print("Button8Clicked")
        ConvMas[3].SetLaserStatus(1)
    def Button9Clicked(self):
        print("Button9Clicked")
        self.ConvBoxDel()
        #ConvMas[4].MissionForTypeDone = 1
        #ConvMas[4].SetLaserStatus(1)
    def Button10Clicked(self):
        print("Button10Clicked")
        SendSerialPortData(self.serialPortScan2, CreateCommandForScaner("800200", "00", "01"), ScanerACK.ReplayData)
        #ConvMas[4].SetLaserStatus(0)

def SendSerialPortData(serialPort, data):
    print("Send " + serialPort.portname + "/*-")
    print(data)
    #dataStr = str(bytearray(data), "ascii")
    #print("Send " + serialPort.portname + ": "+dataStr +" / "+ str(dataStr.encode("ascii").hex()))
    #print("Send " + serialPort.portname + ": " + dataStr + " / " + str(dataStr.encode("ascii").hex()))
    serialPort.WriteQueue.put(data)
    #SetWriteFlag(serialPort, ACKflag)

def CreateCommandForScaner(Opcode, Status, Parameters):
    LRC = 0
    byteOpcode = bytearray.fromhex(Opcode)
    byteStatus = bytearray.fromhex(Status)
    byteParameters = bytearray.fromhex(Parameters)
    Length = str(format(len(byteParameters), '04x'))
    byteLength = bytearray.fromhex(Length)
    HexString = "7e" + Opcode + Status + Length + Parameters
    for i in byteOpcode:
        LRC ^= i
    for i in byteStatus:
        LRC ^= i
    for i in byteLength:
        LRC ^= i
    for i in byteParameters:
        LRC ^= i
    HexString += str(format(LRC,'02x')) + "7E"
    print("Send: "+HexString)
    HexString = bytearray.fromhex(HexString)
    return HexString




def ResetWriteFlag(serialPort):
    #serialPort.WaitACKExFlag = 0
    serialPort.WaitACK = 0

def SetWriteFlag(serialPort, value):
    serialPort.WaitACKExFlag.put(value)

class Stream(QtCore.QObject):
    newText = QtCore.pyqtSignal(str)

    def write(self, text):
        self.newText.emit(str(text))





class ConveyorAsFifo(QtWidgets.QGraphicsPolygonItem):
    def __init__(self, _X, _Y, _ConveyorType, textStr):
        super(ConveyorAsFifo, self).__init__()
        self.ConveyorType = _ConveyorType
        self.BoxList = []
        self.MissionForTypeDone = MissionLevel.Ready
        self.MissionTimeout = 0
        self.motionTimeOut = 10
        self.LaserStatus = 0
        self.PreLaserStatus = 0
        self.motionFlag = 0
        self.ErrorState = 0
        self.BoxLink = None
        self.text = textStr
        self.X = _X
        self.Y = _Y
        self.setPos(QtCore.QPointF(self.X, self.Y))
        self.ConvStopedBrushColor = QtGui.QColor(100, 100, 200)
        self.ConvMotionBrushColor = QtGui.QColor(0, 200, 0)
        self.setBrush(self.ConvStopedBrushColor)
        self.myPolygon = QtGui.QPolygonF(
            [QtCore.QPointF(-AGENT_LENGTH, -AGENT_WIDTH), QtCore.QPointF(AGENT_LENGTH, -AGENT_WIDTH),
             QtCore.QPointF(AGENT_LENGTH, AGENT_WIDTH), QtCore.QPointF(-AGENT_LENGTH, AGENT_WIDTH),
             QtCore.QPointF(-AGENT_LENGTH, -AGENT_WIDTH)])
        self.setPolygon(self.myPolygon)
        if self.ConveyorType == ConvType.NoAction:
            self.MissionForTypeDone = MissionLevel.Ready
    def __repr__(self):
        return("Test()")

    def GetMissionTimeout(self):
        return self.MissionTimeout
    def MissionTimeoutDec(self):
        if self.MissionTimeout > 0:
            self.MissionTimeout -=1
    def SetMissionTimeout(self, value):
        self.MissionTimeout = value
    def GetMissionForTypeDone(self):
        if self.ConveyorType == ConvType.NoAction:
            return MissionLevel.Complit
        else:
            return self.MissionForTypeDone

    def motionTimeOutDec(self):
        if self.motionTimeOut > 0:
            self.motionTimeOut -=1
        #print(self.motionTimeOut)
    def GetTimeOutFlag(self):
        self.motionTimeOutDec()
        if self.motionTimeOut == 0:
            return True
        else:
            return False
    def GetConvBlockState(self):
        if len(self.BoxList) == 0 and self.GetTimeOutFlag():
            #self.MissionTimeout = 10
            return True
        else:
            return False
    def ResetConvStatus(self):
        self.MissionForTypeDone = MissionLevel.Ready
        #self.MissionTimeout = 2000
        self.LaserStatus = 0
        self.PreLaserStatus = 0
        self.motionFlag = 0
        self.update()
    def AddBox(self,_BoxNumber):
        self.BoxList.append(_BoxNumber)
        self.PrintBox(_BoxNumber)
    def RemoveBox(self):
        self.ResetConvStatus()
        self.BoxList.pop(0)
        self.update()
    def SetMotion(self,_motionFlag):
        self.motionFlag = _motionFlag
        if _motionFlag == 0 and self.MissionForTypeDone != MissionLevel.Complit:
            self.motionTimeOut = 10
        self.update()
    def SetLaserStatus(self, _LaserStatus):
        self.PreLaserStatus = self.LaserStatus
        self.LaserStatus = _LaserStatus
        self.update()
    def SetCoord(self, _X, _Y):
        self.X = _X
        self.Y = _Y
        self.setPos(QtCore.QPointF(self.X, self.Y))
        self.update()

    def PrintBox(self,_BoxLink):
        self.update()
        _BoxLink.SetCoord(self.X-AGENT_LENGTH/2, self.Y)

    def UpdateObj(self):
        self.update()

    def paint(self, painter, option, widget=None):
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine))
        if self.motionFlag:
            painter.setBrush(self.ConvMotionBrushColor)
        else:
            painter.setBrush(self.ConvStopedBrushColor)
        painter.drawPolygon(self.myPolygon)
        painter.setPen(QtCore.Qt.black)
        painter.setFont(QtGui.QFont("Times", 18, QtGui.QFont.Bold))
        painter.drawText(QtCore.QPointF(-AGENT_LENGTH + 5, -AGENT_WIDTH + 25), self.text)
        if self.LaserStatus:
            painter.setPen(QtGui.QPen(QtCore.Qt.gray, 3, QtCore.Qt.SolidLine))
        else:
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 3, QtCore.Qt.SolidLine))
        painter.drawLine(40, -AGENT_WIDTH, 40, AGENT_WIDTH)
        painter.drawText(QtCore.QPointF(25, AGENT_WIDTH ), str(len(self.BoxList)))


class Box(QtWidgets.QGraphicsPolygonItem):
    def __init__(self, _conveyorBlockNumber, textStr):
        super(Box, self).__init__()
        self.ID_Number = 0
        self.weight = 0
        self.deltaWeight = 0
        self.TransportFlag = 0
        self.conveyorBlockNumber = []
        self.conveyorBlockNumber.append(_conveyorBlockNumber)
        self.X = 0
        self.Y = 0
        self.biasX = 0
        self.biasY = 0
        if self.biasX > AGENT_LENGTH:
            self.biasX = AGENT_LENGTH
        self.setPos(QtCore.QPointF(self.X + self.biasX, self.Y + self.biasY))
        self.myBrush = QtGui.QColor(100, 100, 200)
        self.setBrush(self.myBrush)
        #self.text = ""#textStr
        self.myPolygon = QtGui.QPolygonF(
            [QtCore.QPointF(-BOX_LENGTH, -BOX_WIDTH), QtCore.QPointF(BOX_LENGTH, -BOX_WIDTH),
             QtCore.QPointF(BOX_LENGTH, BOX_WIDTH), QtCore.QPointF(-BOX_LENGTH, BOX_WIDTH),
             QtCore.QPointF(-BOX_LENGTH, -BOX_WIDTH)])
        self.setPolygon(self.myPolygon)
    def __repr__(self):
        return("123")
    def BoxReset(self):
        self.X = 0
        self.Y = 0
        self.biasX = 0
        self.biasY = 0
    def SetCoord(self, _X, _Y):
        self.X = _X
        self.Y = _Y
        self.setPos(QtCore.QPointF(self.X + self.biasX, self.Y + self.biasY))
        self.update()
    def MoveBox(self, _biasX, _biasY):
        self.biasY = _biasY
        self.biasX = _biasX
        #if self.biasX > AGENT_LENGTH:
        #    self.biasX = AGENT_LENGTH
        #self.setPos(QtCore.QPointF(self.X + self.biasX, self.Y + self.biasY))
        self.update()
    def UpdateObj(self):
        self.update()
    def AddconveyorBlockNumber(self,_conveyorBlockNumber):
        self.conveyorBlockNumber.append(_conveyorBlockNumber)
    def RemoveConveyorFirstBlock(self):
        self.conveyorBlockNumber.pop(0)
    def paint(self, painter, option, widget=None):
        textID = str(self.ID_Number)#''.join(str(e) for e in self.conveyorBlockNumber)
        if len(textID) > 7:
            textID = textID[6:len(textID)-1]
        textWeight = str(self.weight)
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine))
        painter.setBrush(QtCore.Qt.darkYellow)
        painter.drawPolygon(self.myPolygon)
        #painter.addLine(AGENT_WIDTH, AGENT_LENGTH, AGENT_WIDTH+100, AGENT_LENGTH+100)

        painter.setPen(QtCore.Qt.black)
        painter.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        painter.drawText(QtCore.QPointF(-BOX_LENGTH + 10, -BOX_WIDTH + 15), str("{0:4}".format(int(self.ID_Number))))
        painter.drawText(QtCore.QPointF(-BOX_LENGTH + 10, -BOX_WIDTH + 30), textWeight)
        painter.drawText(QtCore.QPointF(-BOX_LENGTH + 10, -BOX_WIDTH + 45), str("{0:.2f}".format(float(self.deltaWeight))))
        #painter.setPen(QtCore.Qt.red)
        #painter.drawLine(80, -BOX_LENGTH-100, 80, BOX_LENGTH+100)
class ServerConnection:
    def __init__(self, sock=None):
        self.sock = None
        self.connected = 0
        self.pings = 0

    def connect(self, host, port):
        try:
            if self.sock is None:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            else:
                self.sock.connect((host, port))
                self.sock.setblocking(0)
                self.send("000,900:\r\n")
                self.connected = 1
                print("Server connection OK")
        except socket.error:
            print("Socket creation failed")
            self.connected = 0

    def reconnect(self):
        if self.connected == 0:
            print("Trying to reconnect")
            if not (self.sock is None):
                self.sock.close()
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connect(SERVER_IP, SERVER_PORT)

    def send(self, msg):
        totalsent = 0
        try:
            while totalsent < len(msg):
                sent = self.sock.send(bytearray(msg[totalsent:].encode("ascii")))
                totalsent = totalsent + sent
                if sent == 0:
                    raise RuntimeError("Socket connection broken")
        # print ("Sucessfully sent %d bytes" % totalsent)

        except socket.error:
            print("Socket send error")
            self.connected = 0

    def receive(self):
        try:
            data = self.sock.recv(1024)
        except socket.error:  # данных нет
            pass  # тут ставим код выхода
        else:  # данные есть
            if len(data) > 0:
                self.parseData(data)

    def parseData(self, data):
        global gModbusInitOk
        need_to_print_data = 1
        data_str = str(data,"ascii")
        #print("ascii text")
        #print(data_str)
        splitted_packets = data_str.split("\n")
        #		print splitted_packets
        for packet in splitted_packets:
            #print("++++++++++++++++++++++++++++")
            #print(packet)
            splitted = packet.split(":")
            #print splitted
            # print len(splitted)
            if data_str.find("ERR") != -1:
                print("ERROR received")
                #gPickShelfPickAutotester.setCurrentState(AUTOTESTER_IDLE)
                #gAgent.setStateToIdle()
                #gAgent.boxId = -1
            if len(splitted) >= 2:
                if splitted[1].find("PNG") != -1:
                    #print("HW received")

                    self.send("000,900:\r\n")
                    need_to_print_data = 0
                    if self.pings < 3:
                        self.pings += 1
                if splitted[1].find("CST") != -1:
                    #print("CST received")
                    if gModbusInitOk==0:
                        # When there is no simulate
                        self.send("000,900:CST,1\r\n")
                    else:
                        #print(len(ConvMas[len(ConvMas)-1].BoxList))
                        if len(ConvMas[-1].BoxList) > 0 and ConvMas[-1].MissionForTypeDone == MissionLevel.Complit and inputs_state[16]==1:
                            self.send("000,900:CST,1\r\n")
                            #print("000,900:CST,1\r\n")
                        else:
                            self.send("000,900:CST,0\r\n")
                            #print("000,900:CST,0\r\n")
                    need_to_print_data = 0
                    if self.pings < 3:
                        self.pings += 1

            if len(splitted) == 3:
                # print splitted[2]
                if splitted[2].find("IDLE") != -1:
                    print("IDLE state received")
                    gAgent.setStateToIdle()
        #if need_to_print_data:
        #   print(data)

    def IsConnected(self):
        return self.connected

    def DecreasePing(self):
        if self.pings > 0:
            self.pings -= 1
        else:
            self.connected = 0

    def GetPings(self):
        return self.pings


def main():
    mainWindow = None
    print("Welcome!")
    data = bytes(GetIdString).decode("latin-1")
    strtmp = ""
    #strtmp = str(GetIdString, "utf-8")



    global gServerConnection
    try:
        gServerConnection = ServerConnection()
    #		gServerConnection.parseData("000,000:@AST:IDLE\n000,000:@AST:IDLE\n");
    # 		gServerConnection.connect("192.168.0.254", 8888) #server
    #		gServerConnection.connect("10.7.3.56", 8888) #Roman
    except:
        print("No connection to transport core server!")


    qtapp = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.setGeometry(20, 150, 1500, 850)
    mainWindow.center()
    mainWindow.show()
    qtapp.exec_()

if __name__ == '__main__':
    main()
