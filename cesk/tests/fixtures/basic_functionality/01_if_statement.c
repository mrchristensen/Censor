#include <stdio.h>
 

int main() {

    int a = 1;
    int b = 3;
    int c = 5;
    int d = 7;
    int e = 11;
    int f = 13;
    int g = 17;
    int h = 19;
    int i = 23;

    int prod = 1;

    if (0 < 1) {
        // should end up here
        prod = prod * a;
    }
    else if (0) {
        prod = prod * b;
    }
    else {
        prod = prod * c;
    }
    
    if (0 > 1) {
        prod = prod * d;
    }
    else if (1) {
        // should end up here
        prod = prod * e;
    }
    else {
        prod = prod * f;
    }

    if (0 > 1) {
        prod = prod * g;
    }
    else if (0) {
        prod = prod * h;
    }
    else {
        // should end up here
        prod = prod * i;
    }

    // should be 1*1*11*23 = 253
    printf("%d\n", prod);
    return 0;
}
