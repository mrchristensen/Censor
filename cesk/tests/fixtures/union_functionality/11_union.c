#include <stdio.h>
//casting int to float
 
union Data {
   int i;
   float f;
   char str[20];
};
 
int main( ) {
   union Data data;
   data.i = 4;
   data.f = 2.26f;
   printf("%d", data.i);

   return 0;
}