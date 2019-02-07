#include <stdio.h>
//Second wonky array test
 
union Data {
   double i;
   float f;
   char str[4];
};
 
int main( ) {
   union Data data;        

    data.f = 56.2f;
   for (int j = 0; j < 4; j++){
       data.str[j] = 'k';
       printf("%c", data.str[j]);
   }
   printf("%f", data.f);
   printf("%f", data.i);

   return 0;
}
