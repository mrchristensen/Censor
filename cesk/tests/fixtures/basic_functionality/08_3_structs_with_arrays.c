#include <stdio.h>

struct array_struct{
    int a[2];
    char buf[10];
};

int main(){
    struct array_struct test;
    test.a[0] = 1;
    test.a[1] = 2;
    test.buf[0] = '3';

    printf("%d",test.a[0]);
    printf("%d",test.a[1]);
    printf("%c",test.buf[0]);
   
    return 0;
}
