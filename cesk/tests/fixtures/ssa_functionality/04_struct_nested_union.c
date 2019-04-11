// Anonymous union inside a struct
// Members of the union should be directly accessible

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

struct a {
	int b;
	struct {
		char i;
		char c;
	};
};// a_name;

int main() {
	//a_name* ac;
	struct a myStruct;
	myStruct.i = "H";
	printf("%c", myStruct.i);
	return 0;
}