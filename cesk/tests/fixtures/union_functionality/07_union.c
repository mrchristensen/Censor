#include <stdio.h>
#include <string.h>
 
union Data {
   int i;
   float f;
   char* str;
};
 
int main( ) {

   union Data data;        
   
   data.str = "Test";   
   printf("%s", data.str);

   return 0;
}