import os
import configparser
from mb import *
from datetime import datetime,date

"""
ivrequest

Escreve 1 na flag de leitura de todos os escravos conectados ao barramento

Solicita,individualmente,que cada um dos dispositivos envie seu conteúdo e 
o armazena em um arquivo de texto.
"""
class Switch:
    def __init__(self, value): 
        self._val = value

    def __enter__(self): 
        return self

    def __exit__(self, type, value, traceback): 
        return False

    def __call__(self, cond, *mconds): 
        return self._val in (cond,)+mconds

def f_help():
    print("""                           IVRequest 0.1                            \n\n
        -h : Mostra este texto de ajuda.
        -u : Atualiza a lista 'slaves.csv' de dispositivos escravos no barramento.\n
        -r : Solicita a todos os escravos no barramento que façam uma leitura, e guarda
             estes resultados em um arquivo .csv por escravo, no diretório './ANO_MÊS_DIA'.
            """)

def f_update():
    slaves = list(range(1,247))
    client.mb.set_response_timeout(0.1)
    for j in range(1,247):
        client.setSlave(j)
        try:
            print(f"Tentando comunicação com o slave {hex(j)}.")
            client.mb.read_input_registers( MbRegisters.VOLTAGE_INIT_REG.value , 1)
            print(f"Slave {hex(j)} respondeu.\n")
        except:
            print(f"Removendo {hex(j)}.\n")
            slaves.remove(j)

    with open("slaves.csv","w") as f:
        f.write( (str(slaves).replace('[','').replace(']','') ))

    print("Lista  salva em 'slaves.csv'!")

def f_read():
    client.setSlave(0x00)                                       #Broadcast
    try:
        client.mb.write_register( MbRegisters.READ_VAL_FLAG.value , 1)
    except:
        pass
    
    try:
        with open("slaves.csv","r") as f:
            slaves = (f.read()).split(',')
    except:
        print("Não foi encontrada uma lista de slaves.Utilize -u para criar uma nova.\n")
        sys.exit(0)
    
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
            with open(f"./{dirName}/{fileNamePrefix}_{hex(int(j))}.csv","w") as f:
                for i in range(0,len(x)):
                    f.write(f"{x[i]},{y[i]}\n")
        except:
            with open(f"./{dirName}/{fileNamePrefix}_{hex(int(j))}.csv","w") as f:
                f.write('IO ERROR.')

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.sections()
   
    if(config.read('ivrequest.ini')):
        pass
    else:
        print("Não foi encontrado um arquivo de configuração.Criando um arquivo padrão.\n")
        with open('ivrequest.ini','w') as f:
            f.write("""#Arquivo de configuração do IV Request
#
#Preenchimento padrão:
[DEFAULT]
Device   = /dev/ttyUSB0
BaudRate = 38400
DataBits = 8
Parity   = N
StopBits = 1
#
            """)
        sys.exit()

    client = ModbusRtuMain  (bytes (config['DEFAULT']['Device'].encode('utf-8')), 
                             int   (config['DEFAULT']['BaudRate']),
                             bytes (config['DEFAULT']['Parity'].encode('utf-8')),
                             int   (config['DEFAULT']['DataBits']),
                             int   (config['DEFAULT']['StopBits'])
                            )
    if(not len(sys.argv) == 2):
        print("Digite uma opção válida. -h para ajuda.")
        sys.exit(0)

    with Switch(sys.argv[1][1::]) as case:
        if   case('h'):
            f_help()
        elif case('u'):
            f_update()
        elif case('r'):
            f_read()
        else:
            print("Digite uma opção válida. -h para ajuda.")

        
                        



    