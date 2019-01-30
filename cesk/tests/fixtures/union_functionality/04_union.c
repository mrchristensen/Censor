#include <stdio.h>
//Test creating two instances of the same union - duplicated node error (which happens because there are on the same line)
 
union Data {
   char str[20];
};
 
int main( ) {

   union Data data1;
   union Data data2;
   return 0;
}