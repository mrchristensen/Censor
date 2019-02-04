#include <stdio.h>
//An array, but something bigger declared before it

union Data {
   int i;
   double j;
   char str[20];
   //int j;
};

int main( ) {
   union Data data1;
   for (int i = 0; i < 20; ++i) { //If we interate to 17 it starts to segfault
      if(i == 0)
      {
         
         data1.str[i] = 'a';
      }
      else if (i == 1)
      {
         data1.str[i] = 'b';
      }
      else
      {
         data1.str[i] = 'c';
      }
      
      if (i > 0)
      {
         printf("%c", data1.str[i]);
      }
   }

   data1.i = 2;
   printf("%d", data1.i);
   data1.j = 3.14;
   printf("%f", data1.j);
   return 0;
}