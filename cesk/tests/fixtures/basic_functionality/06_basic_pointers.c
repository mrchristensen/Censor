#include <stdio.h>
 

int main() {

    int *a;
    int b = 3;
    a = &b;
    *a = 7;
    int temp = *a;
    printf("%d\n", temp);
    return 0;
}
