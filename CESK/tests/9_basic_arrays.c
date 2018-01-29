#include <stdio.h>

int main() {
    int a[10] = {1,1,1,1,1,1,1,1,1,1};
    int sum = 0;
    int i = 0;

    loop: 
		sum = sum + a[i];
		++i;
	if (i < 10) {
		goto loop;
	}

    printf("Sum: %d\n", sum);
    return 0;
}