
import subprocess
import Lib.Common.FileUtils as FU

from enum import auto
from .BaseEnum import BaseEnum

class EChargeCMD( BaseEnum ):
    on      = auto()
    off     = auto()
    Default = on

def controlCharge( chargeCMD, port ):
    # print( f"Charging status:{chargeCMD} port:{port}" ) # дублируется в sh - скрипте
    subprocess.Popen( [ FU.powerBankDir() + "powerControl.sh", port, chargeCMD.toString(), FU.powerBankDir() ] )
