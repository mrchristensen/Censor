#include <stdio.h>
 
int factorial(int n) {
    if (n == 0) {
        return 1;    
    }
    else {
        return n*factorial(n-1);
    }    
}

int main() {
    int n = 7;
    int fact = factorial(n);

	printf("%d\n", fact);
	return 0;
}
