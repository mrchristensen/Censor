#include <stdio.h>
int main() {
    int i[5][2];
    i[3][1] = 1;
    int* j = i;
    int temp1 = j[7];
    printf("%d\n", temp1); 
    return 0;
}
