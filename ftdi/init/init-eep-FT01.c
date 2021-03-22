#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <unistd.h>
#include <getopt.h>
#include <libftdi1/ftdi.h>

#define USB_BUS		1
#define USB_ADDR	4

int read_decode_eeprom(struct ftdi_context *ftdi)
{
    int i, j, f;
    int value;
    int size;
    unsigned char buf[256];

    f = ftdi_read_eeprom(ftdi);
    if (f < 0)
    {
        fprintf(stderr, "ftdi_read_eeprom: %d (%s)\n",
                f, ftdi_get_error_string(ftdi));
        return -1;
    }

    ftdi_get_eeprom_value(ftdi, CHIP_SIZE, & value);
    if (value <0)
    {
        fprintf(stderr, "No EEPROM found or EEPROM empty\n");
        return -1;
    }

    fprintf(stderr, "Chip type %d ftdi_eeprom_size: %d\n", ftdi->type, value);
    if (ftdi->type == TYPE_R)
        size = 0xa0;
    else
        size = value;
    ftdi_get_eeprom_buf(ftdi, buf, size);
    for (i=0; i < size; i += 16)
    {
        fprintf(stdout,"0x%03x:", i);

        for (j = 0; j< 8; j++)
            fprintf(stdout," %02x", buf[i+j]);
        fprintf(stdout," ");
        for (; j< 16; j++)
            fprintf(stdout," %02x", buf[i+j]);
        fprintf(stdout," ");
        for (j = 0; j< 8; j++)
            fprintf(stdout,"%c", isprint(buf[i+j])?buf[i+j]:'.');
        fprintf(stdout," ");
        for (; j< 16; j++)
            fprintf(stdout,"%c", isprint(buf[i+j])?buf[i+j]:'.');
        fprintf(stdout,"\n");
    }

    f = ftdi_eeprom_decode(ftdi, 1);
    if (f < 0)
    {
        fprintf(stderr, "ftdi_eeprom_decode: %d (%s)\n",
                f, ftdi_get_error_string(ftdi));
        return -1;
    }
    return 0;
}

int main(void) {

   struct ftdi_context *ftdi;
   
   if ((ftdi = ftdi_new()) == 0) {
        printf("Failed to allocate ftdi structure :%s \n", ftdi_get_error_string(ftdi));
        return EXIT_FAILURE;
   }

   // select first interface
   ftdi_set_interface(ftdi, INTERFACE_ANY);

   if (ftdi_usb_open_bus_addr(ftdi, USB_BUS, USB_ADDR) < 0) {
      printf("Unable to open device: (%s)", ftdi_get_error_string(ftdi));
   }

   printf("Decoded values of first device:\n");
   read_decode_eeprom(ftdi);

   printf("Init EEPROM values in memory...\n");

   if (ftdi_eeprom_initdefaults(ftdi, "FTDI", "FTDI Quad channel", "FT01") < 0) {
      printf("ftdi_eeprom_initdefaults: ERROR");
      ftdi_free(ftdi);
      return -1;
   }

   if (ftdi_set_eeprom_value(ftdi, CHIP_TYPE, 0x56) < 0) {	// EEPROM : 93x56
      printf("ftdi_set_eeprom_value: (%s)\n", ftdi_get_error_string(ftdi));
      ftdi_free(ftdi);
      return -1;
   }

   if (ftdi_set_eeprom_value(ftdi, USE_SERIAL, 1) < 0) {
      printf("ftdi_set_eeprom_value: (%s)\n", ftdi_get_error_string(ftdi));
      ftdi_free(ftdi);
      return -1;
   }

   if (ftdi_set_eeprom_value(ftdi, SELF_POWERED, 1) < 0) {
      printf("ftdi_set_eeprom_value: (%s)\n", ftdi_get_error_string(ftdi));
      ftdi_free(ftdi);
      return -1;
   }

   if (ftdi_set_eeprom_value(ftdi, MAX_POWER, 0) < 0) {
      printf("ftdi_set_eeprom_value: (%s)\n", ftdi_get_error_string(ftdi));
      ftdi_free(ftdi);
      return -1;
   }

   /*
   if (ftdi_set_eeprom_value(ftdi, CHANNEL_C_RS485, 1) < 0) {
      printf("ftdi_set_eeprom_value: (%s)\n", ftdi_get_error_string(ftdi));
      ftdi_free(ftdi);
      return -1;
   }
   */
   if(ftdi_eeprom_build(ftdi) < 0) {
      printf("ftdi_eeprom_build: (%s)\n", ftdi_get_error_string(ftdi));
      ftdi_free(ftdi);
      return -1;
   }

   printf("Write EEPROM...\n");

   if(ftdi_write_eeprom(ftdi) < 0) {
      printf("ftdi_write_eeprom: (%s)\n", ftdi_get_error_string(ftdi));
      ftdi_free(ftdi);
      return -1;
   } 

   printf("EEPROM write success !\n");

   ftdi_usb_close(ftdi);

   return 0;
}
