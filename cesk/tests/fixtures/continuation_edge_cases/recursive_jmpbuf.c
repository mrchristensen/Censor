#include <stdio.h>
#include <setjmp.h>
jmp_buf buf;
void f(int x)
{
    if (!x)
    {
        printf("\n");
        longjmp(buf, 1);
    }
    else{
        printf("%d",x);
        f(x - 1);
    }
}
int main()
{
    int x = 9;
    setjmp(buf);
    if (x)
        f(x--);
}
