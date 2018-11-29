import os
from mb import *
from time import sleep
from datetime import datetime,date

"""
ivrequest

Escreve 1 na flag de leitura de todos os escravos conectados ao barramento
"""

if __name__ == "__main__":
    client = ModbusRtuMain(b'/dev/ttyUSB0', 38400, b'N', 8, 1)  #Baud=38400, 8N1 
    client.setSlave(0x00)                                       #Broadcast
    try:
        client.mb.write_register( MbRegisters.READ_VAL_FLAG.value , 1)
    except:
        pass
    
   #sleep(2)
    dirName = str( date.today())
    try:
        os.mkdir(dirName)
    except:
        pass

    slaves = list(range(1,11))
    
    client.setSlave(10)
    client.mb.read_input_registers( MbRegisters.VOLTAGE_INIT_REG.value , 1)

    for j in range(1,11):
        client.setSlave(j)
        try:
            client.mb.read_input_registers( MbRegisters.VOLTAGE_INIT_REG.value , 1)
        except:
            print(f"removido {j}")
            slaves.remove(j)

    print(slaves)
    for i in slaves:
        client.setSlave(i)
        try:
            x = list(client.mb.read_input_registers(MbRegisters.VOLTAGE_INIT_REG.value,
                MbRegisters.DATA_REGS.value))
            y = list(client.mb.read_input_registers(MbRegisters.CURRENT_INIT_REG.value, 
                MbRegisters.DATA_REGS.value))
        except:
            with open(f"./{dirName}/{hex(i)}.txt","w") as f:
                f.write('IO ERROR.')

        with open(f"./{dirName}/{datetime.now()}{hex(i)}.txt","w") as f:
                f.write('IO ERROR.')

                        



    