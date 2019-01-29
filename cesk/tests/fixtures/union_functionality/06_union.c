#include <stdio.h>
#include <string.h>
 
union Data {
   int i;
   float f;
   char str[20];
};
 
int main( ) {

   union Data data;        

   for (int j = 0; j < 1; j++) {
      data.str[j] = 'm';
      printf("%c", data.str[j]);
   }

   return 0;
}