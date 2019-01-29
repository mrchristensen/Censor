#include <stdio.h>
#include <string.h>
 
union Data {
   int myInts[20];
};
 
int main( ) {

   union Data data;        
   
   /*for(int i; i < 20; i++){
      data.myInts[i] = i;
      printf("%d", data.myInts[i]);
   }*/

   int i = 0;
   while (i < 19)
   {
      data.myInts[i] = 20;
      printf("%d", data.myInts[i]);
      i++;
   }
   
   return 0;
}