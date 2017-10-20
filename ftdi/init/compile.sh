gcc init-eep-FT01.c -lftdi1 -L/usr/local/lib -I/usr/local/include/libftdi1 -o init-eep-FT01
gcc init-eep-FT02.c -lftdi1 -L/usr/local/lib -I/usr/local/include/libftdi1 -o init-eep-FT02
gcc eeprom.c -lftdi1 -L/usr/local/lib -I/usr/local/include/libftdi1 -o eeprom
