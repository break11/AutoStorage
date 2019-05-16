import unittest

import sys
import os
from collections import deque

sys.path.append( os.path.abspath(os.curdir)  )

from App.AgentsManager.AgentServer_Event import EAgentServer_Event
from App.AgentsManager.AgentServerPacket import CAgentServerPacket, EPacket_Status
from App.AgentsManager.AgentsConnectionServer import _processRxPacket

class Test_processRxPacket(unittest.TestCase):

    def test_Data_packets(self):
        # нормальная ситуация - получение следующего по порядку пакета (без перехода через 999)
        TX_FIFO = deque()
        ACC_cmd = CAgentServerPacket( event=EAgentServer_Event.ServerAccepting, packetN=24 )
        cmd = CAgentServerPacket( event=EAgentServer_Event.BatteryState, packetN=25 )

        testI = 5
        def testF( cmd ):
            nonlocal testI
            testI += cmd.packetN

        _processRxPacket( cmd, ACC_cmd, TX_FIFO, lastTXpacketN=0, processAcceptedPacket=testF )
        self.assertEqual( cmd.status, EPacket_Status.Normal ) # статус пакета - не дубликат
        self.assertEqual( ACC_cmd.packetN, 25 ) # номер пакета подтверждения обновился
        self.assertEqual( testI, 30 ) # функция обработки пакеты была вызвана

        # повторный приход команды с таким же именем считается дубликатом
        _processRxPacket( cmd, ACC_cmd, TX_FIFO, lastTXpacketN=0, processAcceptedPacket=testF )
        self.assertEqual( cmd.status, EPacket_Status.Duplicate )
        self.assertEqual( ACC_cmd.packetN, 25 ) # номер пакета подтверждения не должен поменяться
        # функция обработки пакета НЕ была вызвана второй раз - в тестовом счетчике вызова обработчика команды осталось прежнее значение
        self.assertEqual( testI, 30 )

        # проверка корректной обработки переходов
        testI = 5
        cmd.packetN = 0
        ACC_cmd.packetN = 999
        _processRxPacket( cmd, ACC_cmd, TX_FIFO, lastTXpacketN=0, processAcceptedPacket=testF )
        self.assertEqual( cmd.status, EPacket_Status.Normal ) # статус пакета - не дубликат
        self.assertEqual( ACC_cmd.packetN, 0 ) # номер пакета подтверждения обновился
        self.assertEqual( testI, 5 ) # функция обработки пакеты была вызвана

        _processRxPacket( cmd, ACC_cmd, TX_FIFO, lastTXpacketN=0, processAcceptedPacket=testF )
        self.assertEqual( cmd.status, EPacket_Status.Duplicate )
        self.assertEqual( ACC_cmd.packetN, 0 ) # номер пакета подтверждения не должен поменяться
        # функция обработки пакета НЕ была вызвана второй раз - в тестовом счетчике вызова обработчика команды осталось прежнее значение
        self.assertEqual( testI, 5 )

        # проверка отстающих пакетов
        # рядовой случай
        cmd.packetN = 18
        ACC_cmd.packetN = 20
        testI = 0
        _processRxPacket( cmd, ACC_cmd, TX_FIFO, lastTXpacketN=0, processAcceptedPacket=testF )
        self.assertEqual( cmd.status, EPacket_Status.Error ) # ошибка - номер пакета отстает больше чем на 1 от последнего принятого
        self.assertEqual( ACC_cmd.packetN, 20 ) # номер последнего полученного пакета не меняется
        self.assertEqual( testI, 0 ) # функция обработки пакета НЕ была вызвана
        # случай с переходом
        cmd.packetN = 999
        ACC_cmd.packetN = 1
        _processRxPacket( cmd, ACC_cmd, TX_FIFO, lastTXpacketN=0, processAcceptedPacket=testF )
        self.assertEqual( cmd.status, EPacket_Status.Error ) # ошибка - номер пакета отстает больше чем на 1 от последнего принятого
        self.assertEqual( ACC_cmd.packetN, 1 ) # номер последнего полученного пакета не меняется
        self.assertEqual( testI, 0 ) # функция обработки пакета НЕ была вызвана

        # проверка забегающих вперед пакетов
        # рядовой случай
        cmd.packetN = 22
        ACC_cmd.packetN = 20
        _processRxPacket( cmd, ACC_cmd, TX_FIFO, lastTXpacketN=0, processAcceptedPacket=testF )
        self.assertEqual( cmd.status, EPacket_Status.Error ) # ошибка - номер пакета отстает больше чем на 1 от последнего принятого
        self.assertEqual( ACC_cmd.packetN, 20 ) # номер последнего полученного пакета не меняется
        self.assertEqual( testI, 0 ) # функция обработки пакета НЕ была вызвана
        # случай с переходом
        cmd.packetN = 1
        ACC_cmd.packetN = 999
        _processRxPacket( cmd, ACC_cmd, TX_FIFO, lastTXpacketN=0, processAcceptedPacket=testF )
        self.assertEqual( cmd.status, EPacket_Status.Error ) # ошибка - номер пакета отстает больше чем на 1 от последнего принятого
        self.assertEqual( ACC_cmd.packetN, 999 ) # номер последнего полученного пакета не меняется
        self.assertEqual( testI, 0 ) # функция обработки пакета НЕ была вызвана

    def test_CA_after_HW(self):
        TX_FIFO = deque()
        ACC_cmd = CAgentServerPacket( event=EAgentServer_Event.ServerAccepting )
        cmd = CAgentServerPacket( event=EAgentServer_Event.ClientAccepting, packetN=0 )
        # принимаем корректный CA первый раз - при старте обмена т.к. TX_FIFO будет пустым (инициализация посылки HW не идет через TX_FIFO) 
        # CA получит статус Duplicate - даже первый CA по HW

        _processRxPacket( cmd, ACC_cmd, TX_FIFO, lastTXpacketN=0 )
        self.assertEqual( cmd.status, EPacket_Status.Duplicate )

    def test_CA_Normal_and_Duplicate_in_WorkLoop(self):
        TX_FIFO = deque()
        ACC_cmd = CAgentServerPacket( event=EAgentServer_Event.ServerAccepting, packetN=33 )
        cmd = CAgentServerPacket( event=EAgentServer_Event.ClientAccepting, packetN=1 )
        TX_FIFO.append( CAgentServerPacket( event=EAgentServer_Event.BatteryState, packetN=1 ) )

        # последующие CA будут получать корректный статус при первом получении, т.к. именно при получении CA по команде - эта команда удаляется из буфера отправки
        _processRxPacket( cmd, ACC_cmd, TX_FIFO, lastTXpacketN=1 )

        self.assertEqual( cmd.status, EPacket_Status.Normal ) # статус CA - Normal - распознан первых приход CA по этой команде
        self.assertEqual( len(TX_FIFO), 0 ) # очередь очистила отправленную команду, т.к. получила подтверждение по ней
        self.assertEqual( ACC_cmd.packetN, 33 ) # номер 

        # повторное получение CA будет распознаваться как дубликат
        _processRxPacket( cmd, ACC_cmd, TX_FIFO, lastTXpacketN=1 )
        self.assertEqual( cmd.status, EPacket_Status.Duplicate )

        # проверка перехода через 999
        cmd.packetN = 999
        _processRxPacket( cmd, ACC_cmd, TX_FIFO, lastTXpacketN=0 )
        self.assertEqual( cmd.status, EPacket_Status.Duplicate )

        # рядовой случай получения дубликатов
        cmd.packetN = 20
        _processRxPacket( cmd, ACC_cmd, TX_FIFO, lastTXpacketN=21 )
        self.assertEqual( cmd.status, EPacket_Status.Duplicate )

        # проверка на то, что пакет отстающий больше, чем на 1 - распознается как ошибка
        cmd.packetN = 20 # рядовой случай
        _processRxPacket( cmd, ACC_cmd, TX_FIFO, lastTXpacketN=22 )
        self.assertEqual( cmd.status, EPacket_Status.Error )
        cmd.packetN = 999 # случай с переходом
        _processRxPacket( cmd, ACC_cmd, TX_FIFO, lastTXpacketN=1 )
        self.assertEqual( cmd.status, EPacket_Status.Error )

        # проверка на то, что пакет забегающий вперед распознается как ошибка
        cmd.packetN = 21 # рядовой случай
        _processRxPacket( cmd, ACC_cmd, TX_FIFO, lastTXpacketN=20 )
        self.assertEqual( cmd.status, EPacket_Status.Error )
        cmd.packetN = 22 # рядовой случай
        _processRxPacket( cmd, ACC_cmd, TX_FIFO, lastTXpacketN=20 )
        self.assertEqual( cmd.status, EPacket_Status.Error )
        cmd.packetN = 0 # случай с переходом
        _processRxPacket( cmd, ACC_cmd, TX_FIFO, lastTXpacketN=999 )
        self.assertEqual( cmd.status, EPacket_Status.Error )
        cmd.packetN = 1 # случай с переходом
        _processRxPacket( cmd, ACC_cmd, TX_FIFO, lastTXpacketN=999 )
        self.assertEqual( cmd.status, EPacket_Status.Error )

if __name__ == '__main__':
    unittest.main()