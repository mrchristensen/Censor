#include <stdio.h>
#include <stdlib.h>

int main() {
    int *a = malloc(sizeof(int));
    *a = 3;
    printf("a: %d\n", *a);
}

