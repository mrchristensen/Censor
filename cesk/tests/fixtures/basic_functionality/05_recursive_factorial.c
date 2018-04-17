#include <stdio.h>
 
int factorial(int n) {
    if (n == 0) {
        return 1;    
    }
    else {
        int censor0 = n-1;
        return n*factorial(censor0);
    }    
}

int main() {
    int n = 7;
    int fact = factorial(n);

	printf("%d\n", fact);
	return 0;
}
