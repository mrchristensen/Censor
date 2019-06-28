#include <stdio.h>
//Second wonky array test

union Data {
   int i;
   float f;
   char str[20];
};

int main( ) {
   union Data data;

   data.i = 5;
   printf("%d", data.i);
   data.f = 2.3f;
   printf("%f", data.f);
   for (int j = 0; j < 20; j++) {
      data.str[j] = 'm';
      printf("%c", data.str[j]);
   }

   for (int j = 0; j < 20; j++){
      printf("%c", data.str[j]);
   }

   return 0;
}
