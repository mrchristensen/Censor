#include <stdio.h>
#include <stdlib.h>

int main(){
    int* pointer = (int*)malloc(sizeof(int)*20);
    pointer[0] = 123456789;
    pointer += 100000;
    pointer -= 50000;
    pointer -= 50000;
    int x = *pointer;
    printf("%d\n",x);
    return 0;        
}