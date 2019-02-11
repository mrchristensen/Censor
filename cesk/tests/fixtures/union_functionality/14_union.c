#include <stdio.h>
//Floats and doubles, two variables

union Data {
   double d;
   float f;
};

int main( ) {
    union Data data;
    data.d = 24.3;
   union Data arr[10];
   for (int i = 0; i < 10; i++) {
       arr[i] = data;
       printf("%f", arr[i].d);
   }

   return 0;
}