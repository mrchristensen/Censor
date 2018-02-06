#include <stdio.h>
 

int main() {

	int *a, *b;
    int c = 3, d = 7;

	a = &c;
    b = &d;

    int sum = *a + *b; 
	printf("%d\n", sum);
	return 0;
}
