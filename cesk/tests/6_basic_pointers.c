#include <stdio.h>
 

int main() {

	int *a;
    int b = 3;
	a = &b;
    *a = 7;
	printf("%d\n", *a);
	return 0;
}
