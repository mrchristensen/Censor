#include <stdio.h>
int main(){
    char* s = "abcd";
    int i = *(int*)s;
    printf("0x%x\n",i);
}