#include <modbus.h>
#include<stdio.h>

int main(int argc, char const *argv[])
{
    modbus_t* client;
    int baud = 38400;
    char* device = "/dev/USB0";
    client = modbus_new_rtu("/dev/USB0",baud,'N',8,1);
    printf("%s",stderr);
    modbus_connect(client);
    printf("%s",stderr);
    modbus_set_slave(client,0x0a);
    printf("%s",stderr);
    modbus_write_register(client,2000,4);
    modbus_close(client);
    return 0;
}
