#include <stdio.h>
//

union DataU {
   int *iptr;
};

int main( ) {
   union DataU data;           
   int i = 3;
   int *ptr = &i;
   data.iptr = ptr;
   printf("%d", *(data.iptr));

   return 0;
}