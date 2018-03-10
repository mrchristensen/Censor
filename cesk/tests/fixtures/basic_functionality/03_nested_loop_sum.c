#include <stdio.h>


int main() {

    int m[3][3] = {{1,2,3},{4,5,6},{7,8,9}};
    int i = 0, j = 0;
    int dim = 3;
    int sum = 0;    
    outer: 
        inner: 
            sum = sum + m[i][j];
            i = i + 1;
            if (i < dim) {
                goto inner;
            }
        i = 0;
        j = j + 1;
        if (j < dim) {
            goto outer; 
        }
    printf("%d\n", sum);
    return 0;
}
