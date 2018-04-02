#include <stdio.h>


int main() {

    int m[3][3];
    m[0][0] = 1;
    m[0][1] = 2;
    m[0][2] = 3;
    m[1][0] = 4;
    m[1][1] = 5;
    m[1][2] = 6;
    m[2][0] = 7;
    m[2][1] = 8;
    m[2][2] = 9;

    int i = 0, j = 0;
    int dim = 3;
    int sum = 0;    
    int * censor01;
    outer: 
        inner:; 
	    censor01 = m[i];
            sum = sum + censor01[j];
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
