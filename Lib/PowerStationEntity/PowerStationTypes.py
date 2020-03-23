from enum import Enum, auto

from Lib.Common.BaseEnum import BaseEnum
from Lib.Common.StrProps_Meta import СStrProps_Meta

class PowerStationCommands( metaclass = СStrProps_Meta ):
    GetState       = "SYST:LOCK:OWN?"
    SetRemote      = "SYST:LOCK:STAT 1"
    SetReset       = "*RST"
    GetVoltage     = "MEAS:VOLT?"
    GetCurrent     = "MEAS:CURR?"
    SetPowerOff    = "OUTP OFF"
    SetPowerOn     = "OUTP ON"

    RemoteState  = "REMOTE"
    NoneState    = "NONE"

    @classmethod
    def Voltage(cls, val):
        return f"VOLT {val}"

    @classmethod
    def Current(cls, val):
        return f"CURR {val}"

class EChargeStage( BaseEnum ):
    GetState    = auto()  # Получение состояния
    SetRemote   = auto()  # Переключение на удаленное управление
    SetReset    = auto()  # Сброс
    GetVoltage  = auto()  # Получение напряжения на выходе
    GetCurrent  = auto()  # Получение тока на выходе
    SetPowerOff = auto()  # Отключение выхода
    SetPowerOn  = auto()  # Включение выхода
    SetVoltage  = auto()  # Задать максимальное напряжение на выходе
    SetCurrent  = auto()  # Задать максимальный ток на выходе

    Undefined   = auto()
    Default     = GetState

class EChargeState( BaseEnum ):
    on      = auto()
    off     = auto()

    Undefined = auto()
    Default   = off
