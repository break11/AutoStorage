
import subprocess
import Lib.Common.FileUtils as FU

def controlCharge( chargeCMD, port ):
    # print( f"Charging status:{chargeCMD} port:{port}" ) # дублируется в sh - скрипте
    subprocess.Popen( [ FU.powerBankDir() + "powerControl.sh", port, chargeCMD.toString(), FU.powerBankDir() ] )
