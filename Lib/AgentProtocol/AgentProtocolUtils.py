
from Lib.AgentProtocol.AgentServerPacket import EPacket_Status
from Lib.AgentProtocol.AgentServer_Event import EAgentServer_Event

def getNextPacketN( n ):
    return ( 1 if n == 999 else n+1 )

def _processRxPacket( ACS, cmd, ACC_cmd, TX_FIFO, lastTXpacketN, processAcceptedPacket=None, ACC_Event_OtherSide=EAgentServer_Event.ClientAccepting ):
    # ACS.bSendTX_cmd = True
    # ACS.nReSendTX_Counter = 0
    if cmd.event == ACC_Event_OtherSide:
        assert lastTXpacketN != None # т.к. инициализация по HW прошла, то агент должен существовать

        delta = cmd.packetN - lastTXpacketN

        #всё корректно, пришло CA по текущей активной команде - сносим ее из очереди отправки ( lastTX_N=000 CA_N=000 )
        if delta == 0 or cmd.packetN == 0:
            if len(TX_FIFO) and TX_FIFO[0].packetN == cmd.packetN:
                # пришло подтверждение по текущей активной команде - убираем ее из очереди отправки
                TX_FIFO.popleft()
                cmd.status = EPacket_Status.Normal
                ACS.bSendTX_cmd = True
                ACS.nReSendTX_Counter = 0
            else:
                #видимо, пришло повтороное подтверждение на команду
                cmd.status = EPacket_Status.Duplicate 
            if cmd.packetN == 0:
                cmd.status = EPacket_Status.Normal
        #если разница -1 или 999, это дубликат последней полученной команды ( lastTX_N=001 CA_N=000 ), ( lastTX_N=000 CA_N=999 )
        elif delta == -1 or delta == 998:
            cmd.status = EPacket_Status.Duplicate
        #ошибка(возможно старые пакеты)
        elif delta < -1:
            cmd.status = EPacket_Status.Error
        #ошибка(нумерация пакетов намного больше ожидаемой, возможно была потеря пакетов)
        else:
            cmd.status = EPacket_Status.Error

    else:
        # wantedPacketN - ожидаемый пакет, считаем ожидаемый пакет как последний полученный + 1
        wantedPacketN = getNextPacketN( ACC_cmd.packetN )
        delta = cmd.packetN - wantedPacketN

        # если разница в номерах пакетов 0, то всё корректно
        # так же считаем корректным пакет с входящим кодом 0
        if  delta == 0 or cmd.packetN == 0:
            if cmd.packetN != 0:
                ACC_cmd.packetN = cmd.packetN
            cmd.status = EPacket_Status.Normal
            if processAcceptedPacket is not None:
                processAcceptedPacket( cmd )
            ACS.bSendTX_cmd = True
            ACS.nReSendTX_Counter = 0
        #если разница -1, это дубликат последней полученной команды
        elif delta == -1 or delta == 998:
            cmd.status = EPacket_Status.Duplicate
        #ошибка(возможно старые пакеты)
        elif delta < -1:
            cmd.status = EPacket_Status.Error
        #ошибка(нумерация пакетов намного больше ожидаемой, возможно была потеря пакетов)
        else:
            cmd.status = EPacket_Status.Error
