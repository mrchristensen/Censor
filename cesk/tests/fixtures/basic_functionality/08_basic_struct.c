#include <stdio.h>

struct rectangle {
    int x;
    int y;
};

int main() {
    struct rectangle a = {2, 4};
	int x = a.x;
    printf("%d\n", x);
}
