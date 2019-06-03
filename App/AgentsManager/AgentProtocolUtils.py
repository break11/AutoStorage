
from .AgentServerPacket import CAgentServerPacket, EPacket_Status
from .AgentServer_Event import EAgentServer_Event

from Lib.Common.Utils import wrapSpan, wrapDiv

def getNextPacketN( n ): return ( 1 if n == 999 else n+1 )

def _processRxPacket( ACS, cmd, ACC_cmd, TX_FIFO, lastTXpacketN, processAcceptedPacket=None ):
    if cmd.event == EAgentServer_Event.ClientAccepting:
        assert lastTXpacketN != None # т.к. инициализация по HW прошла, то агент должен существовать ( иначе  )

        delta = cmd.packetN - lastTXpacketN

        #всё корректно, пришло CA по текущей активной команде - сносим ее из очереди отправки ( lastTX_N=000 CA_N=000 )
        if delta == 0:
            if len(TX_FIFO) and TX_FIFO[0].packetN == cmd.packetN:
                # пришло подтверждение по текущей активной команде - убираем ее из очереди отправки
                TX_FIFO.popleft()
                cmd.status = EPacket_Status.Normal
                ACS.bSendTX_cmd = True
                ACS.nReSendTX_Counter = 0
            else:
                #видимо, пришло повтороное подтверждение на команду
                cmd.status = EPacket_Status.Duplicate 
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

        #если 0, то всё корректно 
        if  delta == 0:
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

def agentLogString( agentLink, data ):
    data = wrapDiv( data )
    agentLink.log = agentLink.log + data
    with open( agentLink.sLogFName, 'a' ) as file:
        file.write( data )
    return data

def agentLogPacket( agentLink, thread_UID, packet, bTX_or_RX ):
    data = packet.toBStr( bTX_or_RX=bTX_or_RX, appendLF=False ).decode()
    if agentLink is None:
        print( data )
        return data

    if bTX_or_RX is None:
        sTX_or_RX = ""
        colorTX_or_RX = "#000000"
    elif bTX_or_RX == True:
        sTX_or_RX = "TX:"
        colorTX_or_RX = "#ff0000"
    elif bTX_or_RX == False:
        sTX_or_RX = "RX:"
        colorTX_or_RX = "#283593"

    if packet.status == EPacket_Status.Normal:
        colorsByEvents = { EAgentServer_Event.BatteryState:     "#388E3C",
                            EAgentServer_Event.TemperatureState: "#388E3C",
                            EAgentServer_Event.TaskList:         "#388E3C",
                            EAgentServer_Event.ClientAccepting:  "#1565C0",
                            EAgentServer_Event.ServerAccepting:  "#FF3300", }

        colorData = colorsByEvents.get( packet.event )
        if colorData is None: colorData = "#000000"
    elif packet.status == EPacket_Status.Duplicate:
        colorData = "#999999"
    elif packet.status == EPacket_Status.Error:
        colorData = "#FF0000"

    data = f"{wrapSpan( sTX_or_RX, colorTX_or_RX, 400 )} {wrapSpan( data, colorData )}"

    data = f"T:{ thread_UID } {data}"
    data = wrapDiv( data )

    agentLink.log = agentLink.log + data
    with open( agentLink.sLogFName, 'a' ) as file:
        file.write( data )

    return data

