#include <stdio.h>
//An array, but something bigger declared before it

union Data {
   int i;
   float j;
   char str[20];
};

int main( ) {
   union Data data1;
   //data1.j = 0.2f; //If you write to the float first you pass
   //printf("%f", data1.j);
   //data1.i = 2; //If you write first to the int you segfault
   //If you write to the array you'll mess up the first write
   //printf("%d", data1.i);

   for (int i = 0; i < 20; ++i) { //17 w/ just an int
      if(i == 0){
         data1.str[i] = 'a';
      }
      else if (i == 1){
         data1.str[i] = 'b';
      }
      else{
         data1.str[i] = 'c';
      }
      
      /*if (i > 0){
         printf("%c", data1.str[i]);
      }*/
      printf("%c", data1.str[i]);
   }

   /*for (int i = 0; i < 20; i++){
      printf("%c", data1.str[i]);
   }

   data1.i = 200;
   printf("%d", data1.i);
   data1.j = 3.14f;
   printf("%f", data1.j);*/
   return 0;
}