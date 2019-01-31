#include <stdio.h>
//casting int to float
 
union Data {
   //int i;
   float f;
};
 
int main( ) {
   union Data data;
   //data.i = 4;
   //printf("%d", data.i);

   float myFloat = 1337.66f;        
   data.f = myFloat;
   printf("%f", data.f);
   return 0;
}