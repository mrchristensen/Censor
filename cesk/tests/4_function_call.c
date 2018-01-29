#include <stdio.h>
 
int add2(int n) {
    return n + 2;
}

int main() {
    int n = 7;
    n = add2(n);
    printf("%d\n", n);
	return 0;
}
