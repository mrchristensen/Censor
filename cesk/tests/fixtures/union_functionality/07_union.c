#include <stdio.h>
//Struct in a union

struct nestedStruct {
   int x;
   double y;
};

union Test {
   struct nestedStruct n;
};

int main()
{
   union Test p1;
   p1.n.x = 5;
   p1.n.y = 2.12;

   printf("%d %f", p1.n.x, p1.n.y);
   return 0;
}