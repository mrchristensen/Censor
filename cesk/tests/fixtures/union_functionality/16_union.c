#include <stdio.h>
#include <string.h>

typedef union Data1 {
   int i;
   float f;
   char str[20];
} testTest1;

typedef union Data2{
   int i;
   float f;
   char str[20];
} testTest2;

int socket_cb( ) {

   union Data1 data1;
   union Data2 data2;

   // data.i = 10;
   // data.f = 220.5;
   // strcpy( data.str, "C Programming");

   // printf( "data.i : %d\n", data.i);
   // printf( "data.f : %f\n", data.f);
   // printf( "data.str : %s\n", data.str);

   return 0;
}
//data.i : 1917853763
//data.f : 4122360580327794860452759994368.000000
//data.str : C Programming