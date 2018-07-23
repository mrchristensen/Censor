#include <stdio.h>

typedef struct{
    int x;
    int y;
    int z;
    int a;
} ints;

typedef struct{
    long x;
    long y;
} longs;

int main(){

ints int_struct = {0xDEAD,0xBEAF, 0x92345678,0x7abcdef0};
longs* longs_ptr = (longs*) &int_struct;
printf("%d\n", int_struct.z);
printf("%ld\n",longs_ptr->x);
printf("%ld\n",longs_ptr->y);

return 0;
}
