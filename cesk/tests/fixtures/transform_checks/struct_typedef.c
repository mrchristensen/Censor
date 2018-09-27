#include <stdio.h>
#include <setjmp.h>
typedef int mytype;
struct one
{
    int a;
    jmp_buf b;
    char c;
    mytype e;
};

int main()
{
    struct one tester;
    setjmp(tester.b);
    tester.e = 9;
    printf("%d\n",tester.e);
}