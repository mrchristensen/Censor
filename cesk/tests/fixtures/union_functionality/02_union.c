#include <stdio.h>
#include <string.h>
 
union DataU {
   int i;
   char str[20];
};
 
int main( ) {

   union DataU data;        
   
   for (int i = 0; i < 20; ++i) {
      data.str[i] = 'a';
   }

   return 0;
}