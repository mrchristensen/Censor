#include <stdio.h>

struct Nested {
        int x;
        char *c;
};

union Test {
    struct Nested n;
};

int main()
{
    union Test p1;
    p1.n.x = 5;
    char a = 'a';
    p1.n.c = &a;

    printf("%d %c", p1.n.x, *(p1.n.c));
    return 0;
}