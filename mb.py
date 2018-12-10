#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
# 
# Marcelo Fadini - 2018
#
#

from enum import Enum
from mb_core import *
import sys

class ModbusRtuMain():
    def __init__(self, device , baud, parity, data_bit, stop_bit):
        self.mb = ModbusRtu(device, baud, parity, data_bit, stop_bit)
        try:
            self.mb.connect()
        except:
            print('Sem conexão. Checou permissões, inicialização do programa na placa e conexões físicas?') 
            sys.exit(0)

    def setSlave(self,slave):
        self.mb.set_slave(slave)

    def tearDown(self):
        self.mb.close()

class MbRegisters(Enum):
    VOLTAGE_INIT_REG   =  999
    CURRENT_INIT_REG   = 1049
    VOLTAGE_CONFIG_REG = 1999
    CURRENT_CONFIG_REG = 2000
    READ_VAL_FLAG      = 2001
    DATA_REGS          =   50