#include <stdio.h>
 
union Data {

   char* str;
};
 
int main( ) {

   union Data data1;
   char C = 'C';
   data1.str = &C;
   printf("%c", *data1.str);
   return 0;
}