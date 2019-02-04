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
   printf("%f %f", data.d, data.f);
   return 0;
}