#include <stdio.h>

int main(){

int x = 0x12345678;

int* ptr = &x;

long ptr_value = (long) ptr;

int * ptr2 = (int*) ptr_value;

printf("%d\n",*ptr2);

return 0;

}
