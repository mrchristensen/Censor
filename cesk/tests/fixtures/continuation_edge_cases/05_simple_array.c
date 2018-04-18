#include <stdio.h>
int main() { 
    int a[1];
    int b[1][2];
    a[0] = 5;
    int* temp = b[0];
    temp[1] = 4;
    int temp2 = a[0] + temp[1];
    printf("%d\n",temp2);
    return 0;
}
