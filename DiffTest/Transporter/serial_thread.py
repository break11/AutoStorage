
from time import sleep
from PyQt5.QtCore import * #(QCoreApplication, QObject, QRunnable, QThread, QThreadPool, pyqtSignal)
from PyQt5.QtSerialPort import QSerialPort
from queue import Queue
#import _thread

class WorkerThread(QThread):
    Status = pyqtSignal(str, str)
    dataReady = pyqtSignal(str, str)
    def __init__(self, _portname, _baudrate, _newParsingFlag):
        QThread.__init__(self)
        self.portname = _portname
        self.baudrate = _baudrate
        self.receivedMessage = None
        self.isopen = False
        self.serialport = QSerialPort()
        self.WriteQueue = Queue()
        self.LastPacketError = 0
        self.LastPacket = None
        self.temp = ""
        self.newParsingFlag = _newParsingFlag

    def __del__(self):
        self.wait()

    def run(self):
        self.OpenPort(self.portname, self.baudrate)
        #self.SendDataLoop()
        #self.serialport.readall()

        self.serialport.readyRead.connect(self.newDataInBuffer)
        sleep(1.0)
        self.serialport.clear()
        while self.isRunning():
            sleep(0.01)
            # self.serialport.waitForReadyRead(1)
            # self.CheckAndSendData()

            """
            try:

                if self.isopen:
                    self.serialport.waitForReadyRead(50)
                    self.receivedMessage = self.serialport.readLine()
                    #print(str(self.number)+" "+str(self.receivedMessage))
                    self.number += 1
                    if len(self.receivedMessage) != 0:
                        self.temp = str(self.receivedMessage,"ascii")
                        #print(self.temp)
                        self.dataReady.emit(self._portname, self.temp)
                        #print(self.temp)
                        self.receivedMessage = ""

                self.CheckAndSendData()
            except:
                print("Error reading COM port: ")
            sleep(0.01)
            """

    def newDataInBuffer(self):
        #if self.serialport.canReadLine():
        data = QByteArray
        datastr = ""
        self.receivedMessage = self.serialport.readAll()#.readLine()
        '''
        datastr = self.receivedMessage
        for num in self.receivedMessage:
            data.append(num)
            if num == '\r' or num == '\n':
                self.dataReady.emit(self._portname, data)
                print(data)
        '''
        datastr += str(self.receivedMessage, "latin-1")
        if self._portname == "/dev/serial/by-path/pci-0000:00:14.0-usb-0:9:1.0-port0":
            print("Scan serial data:")
            print(datastr)
        if len(datastr) > 0:
            for n in datastr:
                self.temp += n
                if self.newParsingFlag != None:
                    if (n == '\r' or n == self.newParsingFlag) and len(self.temp) > 1:
                        self.dataReady.emit(self._portname, self.temp)
                        self.temp = ""
                else:
                    if n == '\n' and len(self.temp) > 1:
                        self.dataReady.emit(self._portname, self.temp)
                        self.temp = ""




        #print(self.temp)
        #self.dataReady.emit(self._portname, self.temp)


    def OpenPort(self, sportname, sbaudrate):
        self._portname = sportname
        self.serialport = QSerialPort(sportname)
        self.serialport.setBaudRate(sbaudrate)
        #print(self._portname+": " + str(self.serialport.isOpen()))
        self.serialport.open(QSerialPort.ReadWrite)
        self.isopen = True
        print(str(self._portname)+": "+str(self.serialport.isOpen()))


    def CheckAndSendData(self):

        if not self.WriteQueue.empty():
            data = self.WriteQueue.get()
            self.serialport.writeData(bytearray(data))


    @pyqtSlot(str)
    def WriteDataToPortDirectly(self, data):
        self.WriteQueue.put(data)
        #if self.isopen:
            #self.serialport.write(data.encode('utf-8'))





    @pyqtSlot()
    def myslot(self):
        print("Slot connected")
