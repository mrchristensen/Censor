#include <stdio.h>
//Most simple basecase

union Data {
   int d;
};

int main( ) {

   union Data data;   

   data.d = 3;
   printf("%d", data.d);
   return 0;
}