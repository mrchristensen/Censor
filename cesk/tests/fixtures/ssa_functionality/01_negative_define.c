#include <stdio.h>
#include <string.h>
#include <stdlib.h>

typedef int uint32_t;

void fun(int myInt) {
	return;
}

extern int nla_total_size(int payload);
extern int nla_put_u32(struct nl_msg *, int, uint32_t);

int main() {
	#define TEST 1
	int a = -TEST;
	//uint32_t b = a;
	//int c = nla_total_size(sizeof(a));
	//printf("%d", a);
	//printf("%d", b);
	//printf("%d", c);
	int d = 0;
	switch(a){
	case -TEST:
		d = -TEST;
	break;
	}
	fun(d);
	printf("%d", d);
	return 0;
}