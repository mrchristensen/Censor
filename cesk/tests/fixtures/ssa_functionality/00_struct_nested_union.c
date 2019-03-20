// Anonymous union inside a struct
// Members of the union should be directly accessible

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
	a_name x;
	a_name* abc = &x;
	printf("%d", abc->i);
	return 0;
}