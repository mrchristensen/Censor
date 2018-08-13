#include <stdio.h>
int main() {
	int * x = 0;
	long * y = 0;
	char * c = 0;
	x++;y++;c++;
	printf("%ld\n",(long) x);
	printf("%ld\n",(long) y);
	printf("%ld\n",(long) c);
	return 0;
}
