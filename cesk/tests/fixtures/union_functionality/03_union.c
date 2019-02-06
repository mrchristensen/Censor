#include <stdio.h>
//Single array

union Data {
   char str[10];
};

int main( ) {
   union Data data1;
   for (int i = 0; i < 10; ++i) {
      data1.str[i] = 'a';
      printf("%c", data1.str[i]);
   }
}