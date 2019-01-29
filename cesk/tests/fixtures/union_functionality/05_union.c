#include <stdio.h>
//casting int to float
 
union Data {
   int f;
};
 
int main( ) {
   union Data data;
   float myInt = 1337.66f;        
   printf("%d", data.f);
   data.f = myInt;
   printf("%d", data.f);
   return 0;
}