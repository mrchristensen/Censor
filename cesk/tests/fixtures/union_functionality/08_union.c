#include <stdio.h>
//Union in a struct

union nestedUnion {
   int x;
   float y;
};

struct myStruct {
   union nestedUnion n;
};

int main()
{
   struct myStruct p1;
   p1.n.x = 5;
   p1.n.y = 2.12;

   printf("%d %f", p1.n.x, p1.n.y);
   return 0;
}