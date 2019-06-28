#include <stdio.h>

union Data {
   int myInts[20];
};

int main( ) {

   union Data data;

   int i = 0;
   while (i < 20)
   {
      data.myInts[i] = 20;
      printf("%d", data.myInts[i]);
      i++;
   }

   return 0;
}