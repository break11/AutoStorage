from enum import Enum, auto

from Lib.Common.BaseEnum import BaseEnum

class ECsChangeStage( BaseEnum ):
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

class EChargeCMD( BaseEnum ):
    on      = auto()
    off     = auto()

    Undefined = auto()
    Default   = on
