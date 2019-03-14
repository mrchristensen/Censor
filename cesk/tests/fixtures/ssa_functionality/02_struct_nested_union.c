// Anonymous union inside a struct
// Members of the union should be directly accessible

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

typedef struct a {
	union {
		int i;
	};
} a_name;

int main() {
	a_name aStruct;
	int d = 3;
	aStruct.i = d;
	return 0;
}