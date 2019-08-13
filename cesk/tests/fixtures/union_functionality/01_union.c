#include <stdio.h>
//Floats and doubles, two variables

union Data {
   double d;
   float f;
};

int main( ) {
   union Data data;
   data.d = 3.14;
   data.f = 2.87f;
   printf("%f", data.f);
   return 0;
}

int test(){
   return 0;
}