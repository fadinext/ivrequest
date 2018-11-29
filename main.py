from mb import *

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