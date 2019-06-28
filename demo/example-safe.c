#include <stdio.h>

struct s
{
    int a;
    int b;
    int c;
};


void f(int *x)
{
    printf("%d\n", *(x));
}
int main()
{
    struct s x = {1, 2, 3};
    int* y = &x;
    f(y + 1); // safe
    f(y + 2); // unsafe
    return 0;
}

