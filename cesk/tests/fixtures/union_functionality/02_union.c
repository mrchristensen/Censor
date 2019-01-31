// This test is to see if the union works if there are no other variables declared in the union

#include <stdio.h>
#include <string.h>

union DataU {
   char str[20];
};
 
int main( ) {
   union DataU data;           
   
   for (int i = 0; i < 20; ++i) {
      data.str[i] = 'a';
      printf("%c", data.str[i]);
   }

   return 0;
}