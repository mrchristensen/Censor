#include <stdio.h>
//#include <string.h>
 
union Data {
  // int i;
   //float f;
   double d;
   //char str[20];
};
 
int main( ) {

   union Data data;        

   //data.f = 220.5f;
   data.d = 3.14;


   //printf( "data.i : %d\n", data.i);
   //printf( "data.f : %f\n", data.d);
   //printf( "data.str : %s\n", data.str);

   return 0;
}
//data.i : 1917853763
//data.f : 4122360580327794860452759994368.000000
//data.str : C Programming