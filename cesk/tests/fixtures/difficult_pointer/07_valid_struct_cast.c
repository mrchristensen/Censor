#include <stdio.h>

struct S 
{
    long a;
    int b;
};

void foo(int *x)
{
    printf("%d\n", *x);
}

int main(void)
{
    struct S s;
    s.a = 0xEFBEADDE00000000;
    s.b = 0xFFFFFFFF;
    int *arr = (int *)&s;
    foo(arr + 2);
    return 0;
}

