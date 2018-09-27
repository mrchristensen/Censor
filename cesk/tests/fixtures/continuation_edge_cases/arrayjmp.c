#include <stdio.h>
#include <setjmp.h>
jmp_buf buf[5];
int main(){
    int x = 3;
    if (!setjmp(buf[2]))
    {
        x = 4;
        printf("?");
        longjmp(buf[2], 0);
    }
    else
        printf("!");
    printf("%d\n",x);
}