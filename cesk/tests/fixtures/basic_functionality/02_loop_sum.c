#include <stdio.h>
 
int main() {

	int i = 1;

	int sum = 0;
	loop:
		sum = sum + i;
		i = i + 1;
	if (i <= 10) {
		goto loop;
	}	
	
	printf("%d\n", sum);
	return 0;
}
