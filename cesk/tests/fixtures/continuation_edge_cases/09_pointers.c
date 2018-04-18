#include <stdio.h>

int main() {
    int a[30];
    int i = 5;
    int* j = &i;
    int temp1 = *j;
    printf("%d\n",temp1);
    return 0;
}
