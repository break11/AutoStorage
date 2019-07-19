#!/usr/bin/python3.7

import unittest

import sys
import os
from collections import deque

sys.path.append( os.path.abspath(os.curdir)  )

from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event
from Lib.AgentProtocol.AgentServerPacket import CAgentServerPacket, EPacket_Status
from Lib.AgentProtocol.AgentProtocolUtils import _processRxPacket
from Lib.AgentProtocol.AgentServer_Link import CAgentServer_Link
from Lib.AgentProtocol.AgentServer_Net_Thread import CAgentServer_Net_Thread

class CDummyAgentLink( CAgentServer_Link ):
    pass

class CDummyAgentThread( CAgentServer_Net_Thread ):
    pass

class Test_processRxPacket(unittest.TestCase):

    def test_Data_packets(self):
        # нормальная ситуация - получение следующего по порядку пакета (без перехода через 999)
        DAL = CDummyAgentLink( 555, True )
        DAT = CDummyAgentThread()
        socketDescriptor = self
        ACS = self
        DAT.initAgentServer( socketDescriptor, ACS )
        DAL.last_RX_packetN = 24
        cmd = CAgentServerPacket( event=EAgentServer_Event.BatteryState, packetN=25 )

        testI = 5
        def testF( cmd ):
            nonlocal testI
            testI += cmd.packetN

        _processRxPacket( DAL, DAT, cmd, processAcceptedPacket=testF  )
        self.assertEqual( cmd.status, EPacket_Status.Normal ) # статус пакета - не дубликат
        self.assertEqual( DAL.last_RX_packetN, 25 ) # номер пакета подтверждения обновился
        self.assertEqual( DAL.ACC_cmd.packetN, 25 )
        self.assertEqual( testI, 30 ) # функция обработки пакеты была вызвана
        self.assertEqual( DAT.bSendTX_cmd, True ) # т.к. пришла верная команда, флаг немедленной отправки сообщения выставляется
        self.assertEqual( DAT.nReSendTX_Counter, 0 ) # и сбрасывется счетчик повторной отправки

        # повторный приход команды с таким же именем считается дубликатом
        _processRxPacket( DAL, DAT, cmd, processAcceptedPacket=testF  )
        self.assertEqual( cmd.status, EPacket_Status.Duplicate )
        self.assertEqual( DAL.ACC_cmd.packetN, 25 ) # номер пакета подтверждения не должен поменяться
        # функция обработки пакета НЕ была вызвана второй раз - в тестовом счетчике вызова обработчика команды осталось прежнее значение
        self.assertEqual( testI, 30 )

        # проверка корректной обработки переходов
        testI = 5
        cmd.packetN = 1
        DAL.ACC_cmd.packetN = 999
        _processRxPacket( DAL, DAT, cmd, processAcceptedPacket=testF  )
        self.assertEqual( cmd.status, EPacket_Status.Normal ) # статус пакета - не дубликат
        self.assertEqual( DAL.ACC_cmd.packetN, 1 ) # номер пакета подтверждения обновился
        self.assertEqual( testI, 6 ) # функция обработки пакеты была вызвана

        _processRxPacket( DAL, DAT, cmd, processAcceptedPacket=testF  )
        self.assertEqual( cmd.status, EPacket_Status.Duplicate )
        self.assertEqual( DAL.ACC_cmd.packetN, 1 ) # номер пакета подтверждения не должен поменяться
        # функция обработки пакета НЕ была вызвана второй раз - в тестовом счетчике вызова обработчика команды осталось прежнее значение
        self.assertEqual( testI, 6 )

        # проверка отстающих пакетов
        # рядовой случай
        cmd.packetN = 18
        DAL.ACC_cmd.packetN = 20
        testI = 0
        _processRxPacket( DAL, DAT, cmd, processAcceptedPacket=testF  )
        self.assertEqual( cmd.status, EPacket_Status.Error ) # ошибка - номер пакета отстает больше чем на 1 от последнего принятого
        self.assertEqual( DAL.ACC_cmd.packetN, 20 ) # номер последнего полученного пакета не меняется
        self.assertEqual( testI, 0 ) # функция обработки пакета НЕ была вызвана
        # случай с переходом
        cmd.packetN = 999
        DAL.ACC_cmd.packetN = 1
        _processRxPacket( DAL, DAT, cmd, processAcceptedPacket=testF  )
        self.assertEqual( cmd.status, EPacket_Status.Error ) # ошибка - номер пакета отстает больше чем на 1 от последнего принятого
        self.assertEqual( DAL.ACC_cmd.packetN, 1 ) # номер последнего полученного пакета не меняется
        self.assertEqual( testI, 0 ) # функция обработки пакета НЕ была вызвана

        # проверка забегающих вперед пакетов
        # рядовой случай
        cmd.packetN = 22
        DAL.ACC_cmd.packetN = 20
        _processRxPacket( DAL, DAT, cmd, processAcceptedPacket=testF  )
        self.assertEqual( cmd.status, EPacket_Status.Error ) # ошибка - номер пакета отстает больше чем на 1 от последнего принятого
        self.assertEqual( DAL.ACC_cmd.packetN, 20 ) # номер последнего полученного пакета не меняется
        self.assertEqual( testI, 0 ) # функция обработки пакета НЕ была вызвана
        # случай с переходом
        cmd.packetN = 2
        DAL.ACC_cmd.packetN = 999
        _processRxPacket( DAL, DAT, cmd, processAcceptedPacket=testF  )
        # _processRxPacket( CDummyACS, cmd, ACC_cmd, TX_FIFO, lastTXpacketN=0, processAcceptedPacket=testF )
        self.assertEqual( cmd.status, EPacket_Status.Error ) # ошибка - номер пакета отстает больше чем на 1 от последнего принятого
        self.assertEqual( DAL.ACC_cmd.packetN, 999 ) # номер последнего полученного пакета не меняется
        self.assertEqual( testI, 0 ) # функция обработки пакета НЕ была вызвана

    def test_CA_after_HW(self):
        DAL = CDummyAgentLink( 555, True )
        DAT = CDummyAgentThread()
        socketDescriptor = self
        ACS = self
        DAT.initAgentServer( socketDescriptor, ACS )

        cmd = CAgentServerPacket( event=EAgentServer_Event.ClientAccepting, packetN=0 )
        # принимаем корректный CA первый раз - при старте обмена т.к. TX_FIFO будет пустым
        # CA получит статус Normal - т.к. номер пакета был 0

        _processRxPacket( DAL, DAT, cmd )
        self.assertEqual( cmd.status, EPacket_Status.Normal )

        _processRxPacket( DAL, DAT, cmd )
        self.assertEqual( cmd.status, EPacket_Status.Normal )

        cmd = CAgentServerPacket( event=EAgentServer_Event.ClientAccepting, packetN=1 )
        _processRxPacket( DAL, DAT, cmd )
        self.assertEqual( cmd.status, EPacket_Status.Duplicate )

        # DAL.last_RX_packetN = 1
        DAL.TX_Packets.append( CAgentServerPacket( event=EAgentServer_Event.BatteryState, packetN=2 ) )
        DAL.lastTXpacketN = 2
        cmd = CAgentServerPacket( event=EAgentServer_Event.ClientAccepting, packetN=2 )
        _processRxPacket( DAL, DAT, cmd )
        self.assertEqual( cmd.status, EPacket_Status.Normal )

    def test_CA_Normal_and_Duplicate_in_WorkLoop(self):
        DAL = CDummyAgentLink( 555, True )
        DAT = CDummyAgentThread()

        DAL.TX_Packets.append( CAgentServerPacket( event=EAgentServer_Event.BatteryState, packetN=1 ) )
        DAT.bSendTX_cmd = False
        DAT.nReSendTX_Counter = 20

        socketDescriptor = self
        ACS = self
        DAT.initAgentServer( socketDescriptor, ACS )
        DAL.ACC_cmd.packetN=33

        cmd = CAgentServerPacket( event=EAgentServer_Event.ClientAccepting, packetN=1 )
        # последующие CA будут получать корректный статус при первом получении, т.к. именно при получении CA по команде - эта команда удаляется из буфера отправки
        _processRxPacket( DAL, DAT, cmd )

        self.assertEqual( cmd.status, EPacket_Status.Normal ) # статус CA - Normal - распознан первых приход CA по этой команде
        self.assertEqual( len(DAL.TX_Packets), 0 ) # очередь очистила отправленную команду, т.к. получила подтверждение по ней
        self.assertEqual( DAL.ACC_cmd.packetN, 33 ) # номер
        self.assertEqual( DAT.bSendTX_cmd, True ) # т.к. пришла верная команда, флаг немедленной отправки сообщения выставляется
        self.assertEqual( DAT.nReSendTX_Counter, 0 ) # и сбрасывется счетчик повторной отправки

        # повторное получение CA будет распознаваться как дубликат
        _processRxPacket( DAL, DAT, cmd )
        self.assertEqual( cmd.status, EPacket_Status.Duplicate )

        # проверка перехода через 999
        cmd.packetN = 999
        _processRxPacket( DAL, DAT, cmd )
        self.assertEqual( cmd.status, EPacket_Status.Duplicate )

        # рядовой случай получения дубликатов
        cmd.packetN = 20
        DAL.lastTXpacketN = 21
        _processRxPacket( DAL, DAT, cmd )
        self.assertEqual( cmd.status, EPacket_Status.Duplicate )

        # проверка на то, что пакет отстающий больше, чем на 1 - распознается как ошибка
        DAL.lastTXpacketN = 22
        cmd.packetN = 20 # рядовой случай
        _processRxPacket( DAL, DAT, cmd )
        self.assertEqual( cmd.status, EPacket_Status.Error )
        cmd.packetN = 999 # случай с переходом
        DAL.lastTXpacketN = 2
        _processRxPacket( DAL, DAT, cmd )
        self.assertEqual( cmd.status, EPacket_Status.Error )

        # проверка на то, что пакет забегающий вперед распознается как ошибка
        cmd.packetN = 21 # рядовой случай
        DAL.lastTXpacketN = 20
        _processRxPacket( DAL, DAT, cmd )
        self.assertEqual( cmd.status, EPacket_Status.Error )
        cmd.packetN = 22 # рядовой случай
        DAL.lastTXpacketN = 20
        _processRxPacket( DAL, DAT, cmd )
        self.assertEqual( cmd.status, EPacket_Status.Error )
        cmd.packetN = 0 # случай с переходом
        cmd.lastTXpacketN = 999
        _processRxPacket( DAL, DAT, cmd )
        self.assertEqual( cmd.status, EPacket_Status.Normal )
        cmd.packetN = 1 # случай с переходом
        cmd.lastTXpacketN = 999
        _processRxPacket( DAL, DAT, cmd )
        self.assertEqual( cmd.status, EPacket_Status.Error )

if __name__ == '__main__':
    unittest.main()
