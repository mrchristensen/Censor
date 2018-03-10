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

    if (0 < 1)	return 0;
    
    else if (0) {
        prod *= b;
    }
    else {
        prod *= c;
    }
    
    if (0 > 1) {
        prod *= d;
    }
    else if (1) {
        // should end up here
        prod *= e;
    }
    else {
        prod *= f;
    }

    if (0 > 1) {
        prod *= g;
    }
    else if (0) {
        prod *= h;
    }
    else {
        // should end up here
        prod *= i;
    }

    // should be 1*1*11*23 = 253
    printf("%d\n", prod);
    return 0;
}
