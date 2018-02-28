#include <stdio.h>

int main() {
    int a = 0;
    a = 2 + a;
    printf("%d\n",a);
    a = a + 2;
    printf("%d\n",a);
    a = 2 * a + 3;
    printf("%d\n",a);
    a = (2 * 2 + 3 + 2 * 2)/2;
    printf("%d\n",a);
    return 0;
}
