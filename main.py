import os
from mb import *
from time import sleep
from datetime import datetime,date

"""
ivrequest

Escreve 1 na flag de leitura de todos os escravos conectados ao barramento

Solicita,individualmente,que cada um dos dispositivos envie seu conteúdo e 
o armazena em um arquivo de texto.
"""

if __name__ == "__main__":
    client = ModbusRtuMain(b'/dev/ttyUSB0', 38400, b'N', 8, 1)  #Baud=38400, 8N1 
    client.setSlave(0x00)                                       #Broadcast
    try:
        client.mb.write_register( MbRegisters.READ_VAL_FLAG.value , 1)
    except:
        pass
    
    try:
        with open("slaves.txt","r") as f:
            slaves = (f.read()).split(',')
        sleep(1)
    except:
        print("Não foi encontrada uma lista de slaves. Criando nova.\n")
        slaves = list(range(1,247))
        client.mb.set_response_timeout(0.08)
        for j in range(1,247):
            client.setSlave(j)
            try:
                print(f"Tentando comunicação com o slave {hex(j)}.")
                client.mb.read_input_registers( MbRegisters.VOLTAGE_INIT_REG.value , 1)
                print(f"Slave {hex(j)} respondeu.\n")
            except:
                print(f"Removendo {hex(j)}.\n")
                slaves.remove(j)
        with open("slaves.txt","w") as f:
                f.write( (str(slaves).replace('[','').replace(']','') ))
    
    dirName = str(date.today())
    fileNamePrefix = (datetime.now()).strftime("%Y-%m-%d_%H-%M-%S")

    try:
        os.mkdir(dirName)
    except:
        pass

    client.mb.set_response_timeout(0.5)
    for j in slaves:
        client.setSlave(int(j))
        try:
            x = list(client.mb.read_input_registers(MbRegisters.VOLTAGE_INIT_REG.value,
                MbRegisters.DATA_REGS.value))
            y = list(client.mb.read_input_registers(MbRegisters.CURRENT_INIT_REG.value, 
                MbRegisters.DATA_REGS.value))
            with open(f"./{dirName}/{fileNamePrefix}_{hex(int(i))}.txt","w") as f:
                for i in range(0,len(x)):
                    f.write(f"{x[i]},{y[i]}\n")
        except:
            with open(f"./{dirName}/{fileNamePrefix}_{hex(int(i))}.txt","w") as f:
                f.write('IO ERROR.')

        
                        



    