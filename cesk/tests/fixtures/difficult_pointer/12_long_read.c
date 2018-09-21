#include <stdio.h>
int main(){
    int i[2];
    i[0] = 0xdddddddd;
    i[1] = 0x7bcdabcd;
    long* l = (long*) i;
    printf("%ld\n",*l);
}