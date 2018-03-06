#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int x;
    int y;
} rectangle;

rectangle* makeRectangle(int x, int y) {
    rectangle *r = (rectangle*)malloc(sizeof(rectangle));
    r->x = x;
    r->y = y;
    return r;
}

int main() {
    rectangle *a = makeRectangle(2, 4);
	int x = a->x;
    printf("%d\n", x);
    return 0;
}

