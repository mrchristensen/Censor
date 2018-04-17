#include <stdio.h>

int getFive() {
    return 5;
}

int add(int a, int b) {
    int sum = a + b;
    printf("%d\n", a);
    return sum;
}

int main() {
    int i = getFive();
    printf("%d\n", i);
    i = add(3, 7);
    printf("%d\n", i);
    return 0;
}
