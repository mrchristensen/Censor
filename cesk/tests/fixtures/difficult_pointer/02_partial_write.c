#include <stdio.h>

int main(){
int x = 0x12345678;
short y = 0x4321;
short* ptr = ((void*)&x) + 1;
*ptr = y;
printf("x = %d\n",x);
return 0;
}
