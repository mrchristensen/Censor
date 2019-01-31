#include <stdio.h>
//#include <string.h>
 
union Data {
   double d;
};
 
int main( ) {

   union Data data;        

   data.d = 3.14;

   return 0;
}
