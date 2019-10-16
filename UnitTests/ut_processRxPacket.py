#!/usr/bin/python3.7

import unittest

import weakref
import sys
import os
from collections import deque

sys.path.append( os.path.abspath(os.curdir)  )

from PyQt5.QtNetwork import QTcpSocket

from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event
from Lib.AgentProtocol.AgentServerPacket import CAgentServerPacket, EPacket_Status
from Lib.AgentProtocol.AgentProtocolUtils import _processRxPacket, calcNextPacketN
from Lib.AgentProtocol.AgentServer_Link import CAgentServer_Link
from Lib.AgentProtocol.AgentServer_Net_Thread import CAgentServer_Net_Thread

class CDummyAgentLink( CAgentServer_Link ):
    pass

class CDummyAgentThread( CAgentServer_Net_Thread ):
    def __init__( self ):
        super().__init__()

        # в процессе теста будут сообщения "QIODevice::write (QTcpSocket): device not open", т.к. будут пытаться слаться АКИ на полученные команды
        # но сокет не открыт, т.к. в этом тесте нам это не важно
        self.tcpSocket = QTcpSocket() 

class Test_processRxPacket(unittest.TestCase):

    def test_CalcNextPacketN(self):
        packetN = 1
        n = calcNextPacketN( packetN )
        self.assertEqual( n, 2 )

        packetN = 999
        n = calcNextPacketN( packetN )
        self.assertEqual( n, 1 )

    def test_Data_packets(self):
        # нормальная ситуация - получение следующего по порядку пакета (без перехода через 999)
        DAL = CDummyAgentLink( 555 )
        DAT = CDummyAgentThread()
        socketDescriptor = self
        ACS = self
        DAT.initAgentServer( socketDescriptor, ACS )
        DAT._agentLink = weakref.ref( DAL )
        DAL.last_RX_packetN = 24
        cmd = CAgentServerPacket( event=EAgentServer_Event.BatteryState, packetN=25 )

        testI = 5
        def testF( cmd ):
            nonlocal testI
            testI += cmd.packetN

        _processRxPacket( DAL, DAT, cmd, handler=testF  )
        self.assertEqual( cmd.status, EPacket_Status.Normal ) # статус пакета - не дубликат
        self.assertEqual( DAL.last_RX_packetN, 25 ) # номер пакета подтверждения обновился
        self.assertEqual( DAL.ACC_cmd.packetN, 25 ) # last_RX_packetN - propertyt to DAL.last_RX_packetN
        self.assertEqual( testI, 30 ) # функция обработки пакеты была вызвана

        # повторный приход команды с таким же номером считается дубликатом
        _processRxPacket( DAL, DAT, cmd, handler=testF  )
        self.assertEqual( cmd.status, EPacket_Status.Duplicate )
        self.assertEqual( DAL.ACC_cmd.packetN, 25 ) # номер пакета подтверждения не должен поменяться
        # функция обработки пакета НЕ была вызвана второй раз - в тестовом счетчике вызова обработчика команды осталось прежнее значение
        self.assertEqual( testI, 30 )

        # проверка корректной обработки следующего пакета - номер любой, необязательно по порядку
        testI = 5
        cmd.packetN = 1
        _processRxPacket( DAL, DAT, cmd, handler=testF  )
        self.assertEqual( cmd.status, EPacket_Status.Normal ) # статус пакета - не дубликат
        self.assertEqual( DAL.ACC_cmd.packetN, 1 ) # номер пакета подтверждения обновился
        self.assertEqual( testI, 6 ) # функция обработки пакеты была вызвана

    def test_CA_Normal_and_Duplicate_in_WorkLoop(self):
        DAL = CDummyAgentLink( 555 )
        DAT = CDummyAgentThread()

        DAL.TX_Packets.append( CAgentServerPacket( event=EAgentServer_Event.BatteryState, packetN=1 ) )

        socketDescriptor = self
        ACS = self
        DAT.initAgentServer( socketDescriptor, ACS )
        DAL.ACC_cmd.packetN=33

        cmd = CAgentServerPacket( event=EAgentServer_Event.Accepted, packetN=1 )
        # при получении CA по команде - эта команда удаляется из буфера отправки
        _processRxPacket( DAL, DAT, cmd )

        self.assertEqual( cmd.status, EPacket_Status.Normal ) # статус CA - Normal - распознан первый приход CA по этой команде
        self.assertEqual( len(DAL.TX_Packets), 0 ) # очередь очистила отправленную команду, т.к. получила подтверждение по ней
        self.assertEqual( DAL.ACC_cmd.packetN, 33 ) # номер нашего ACC никак не связан с пришедшим ACC

        # повторное получение CA будет распознаваться как дубликат
        _processRxPacket( DAL, DAT, cmd )
        self.assertEqual( cmd.status, EPacket_Status.Duplicate )

if __name__ == '__main__':
    unittest.main()
