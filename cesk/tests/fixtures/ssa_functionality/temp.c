#include <stdio.h>
#include <string.h>
#include <stdlib.h>

typedef struct a {
	int b;
	union {
		int i;
		char c;
	};
} a_name;

int main() {
	a_name* a;
	printf("%x", a->i);
	return 0;
}