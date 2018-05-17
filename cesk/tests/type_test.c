#include <stdio.h>
int main() {
	int f = 66;
	unsigned char* z = (unsigned char*) &f;
	unsigned char c = *z;
	printf("%d\n", c);
	return 0;
}
