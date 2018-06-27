#include <stdio.h>
 
int factorial(int n) {
    if (n == 0) {
        return 1;    
    }
    else {
        int censor0 = n-1;
        int temp = factorial(censor0);    
        printf("%d\n",temp);
        return n*temp;
    }
}

int main() {
    int n = 7;
    int fact = factorial(n);

	printf("%d\n", fact);
	return 0;
}
