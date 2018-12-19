#include <stdio.h>
#include <stdlib.h>

#include <string.h>
#include <time.h>
#include <malloc.h>
#include <unistd.h>
#include <errno.h>

#include <sys/types.h>
#include <sys/stat.h>

#include <modbus.h>

#define MAX_SLAVES 248
#define SLAVES_LIST "slaves.bin"
#define N_DATA_REGS 50
#define VOLTAGE_INIT_REG 999
#define CURRENT_INIT_REG 1049
#define READ_VAL_FLAG 2001

#define DEVICE "/dev/ttyUSB0"
#define BAUD    38400
#define PARITY  'N'
#define DATA_BITS 8   
#define STOP_BITS 1

int update_slaves(modbus_t* client);
int read_from_slaves(modbus_t* client);
int help_text();
struct timeval response_timeout;

int main(int argc, char const *argv[])
{
    modbus_t* client;
    char op[2];

    client = modbus_new_rtu(DEVICE,BAUD,PARITY,DATA_BITS,STOP_BITS);
    modbus_connect(client);

    if (modbus_connect(client) == -1) 
    {
        fprintf(stderr, "Connection failed: %s\n", modbus_strerror(errno));
        modbus_free(client);
    return -1;
    }

    sprintf(op,"%s",argv[1]);

    switch(op[1])
    {
        case 'h':
            help_text();
            break;
        case 'u':
            update_slaves(client);
            break;
        case 'r':
            read_from_slaves(client);
            break;
        default:
            printf("Selecione uma opção válida. -h para ajuda.\n");
            break;
    }
    modbus_close(client);
    modbus_free(client);
    return 0;
}

int update_slaves(modbus_t* client)
{
    FILE* slaves;
    int i;
    uint8_t aux[MAX_SLAVES];
    for(i=0;i<MAX_SLAVES;i++)
        aux[i] = i;

    uint16_t* dest;
    dest = malloc(sizeof(uint16_t));

    response_timeout.tv_sec = 0;
    response_timeout.tv_usec = 80000;
    //modbus_set_response_timeout(client,&response_timeout);
    modbus_set_response_timeout(client,0, 80000);

    for(i=1;i<MAX_SLAVES;i++)
    {
        modbus_set_slave(client,i);
        printf("Tentando comunicação com o slave 0x%x.\n",i);
        if(modbus_read_registers(client, 1999 , 1 , dest) == -1)
        {
            aux[i] = 0;
            printf("Removendo 0x%x.\n",i);
            fprintf(stderr,"%s\n",modbus_strerror(errno));
        }
        else
            printf("Slave 0x%x respondeu.\n\n",i);
    }

    slaves = fopen(SLAVES_LIST,"wb");
    for(i=1; i<MAX_SLAVES; i++)
    {
        if (aux[i] != 0)
            fwrite(&aux[i], 1, sizeof(uint8_t), slaves);
    } 
    fclose(slaves);
    free(dest);
    return 0;
}

int read_from_slaves(modbus_t* client)
{   
    FILE* slaves;
    FILE* output;
    char filename[100];
    char dirname [100];
    char aux[100];
    int i,j;

    uint8_t slaves_count;
    uint8_t slaves_list[MAX_SLAVES] = {0,0,0,0};

    uint16_t* x,*y;

    time_t t = time(NULL);
    struct tm tm = *localtime(&t);
    struct stat st = {0};

    sprintf(&dirname[0], "%d-%d-%d", tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday);
    
    if (stat(dirname, &st) == -1) 
        mkdir(dirname, 0700);
    
    slaves = fopen(SLAVES_LIST,"rb");

    fseek(slaves, 0 , SEEK_END);
    slaves_count = ftell(slaves);

    fseek(slaves, 0 , SEEK_SET);
    fread(&slaves_list,sizeof(uint8_t), slaves_count, slaves);

    modbus_set_slave(client,0x00);
    modbus_write_register(client,READ_VAL_FLAG,1);

    x = malloc(N_DATA_REGS * sizeof(uint16_t));
    y = malloc(N_DATA_REGS * sizeof(uint16_t));

    response_timeout.tv_sec = 1;
    response_timeout.tv_usec = 0;

    //modbus_set_response_timeout(client,&response_timeout);
    modbus_set_response_timeout(client,1,0);

    i = 0;
    while(slaves_list[i] != 0)
    {
        modbus_set_slave(client,slaves_list[i]);

        if(modbus_read_input_registers(client, VOLTAGE_INIT_REG , N_DATA_REGS , x) ==  -1)
        {
            fprintf(stderr,"%s\n",modbus_strerror(errno)); 
            break;
        }
            
        if(modbus_read_input_registers(client, CURRENT_INIT_REG , N_DATA_REGS , y) ==  -1)
        {
            fprintf(stderr,"%s\n",modbus_strerror(errno));
            break;
        }
            
        sprintf(&filename[0], "%s", dirname);
        sprintf(aux,"_%d-%d-%d_0x",tm.tm_hour,tm.tm_min,tm.tm_sec);
        sprintf(&filename[0], "%s%s", filename, aux);
        sprintf(aux,"%x.csv", slaves_list[i]);
        sprintf(&filename[0], "%s%s", filename, aux);

        sprintf(aux,"%s/%s",dirname,filename);

        output = fopen(aux,"wt");
        for(j=0;j<N_DATA_REGS;j++)
            fprintf(output,"%d,%d\n",x[j],y[j]);

        fclose(output);  
        i++;
    }
    fclose(slaves);
    free(x);
    free(y);
    return 0;
}

int help_text()
{
    printf("""IV REQUEST 0.1\n\
    Uso:\n\
    -u: Atualiza a lista de slaves no arquivo slaves.bin. \n\
    -r: Realiza uma leitura em todos os slaves e salva em um arquivo csv.\n\
    -h: Mostra este texto de ajuda.\n\n""");
    return 0;
}
