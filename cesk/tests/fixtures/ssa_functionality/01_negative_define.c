#include <stdio.h>
#include <string.h>
#include <stdlib.h>

void fun(int myInt) {
	return;
}

int main() {
	#define TEST 1
	int a = -TEST;
	printf("%d", a);
	fun(-TEST);
	return 0;
}