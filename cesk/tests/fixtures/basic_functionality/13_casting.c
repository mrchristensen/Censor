struct A {
    int x;
    float y;
};

struct B {
    float x;
    int y;
};

int main() {
    // char c = 5;
    // short s = (short) c;
    // int i = (int) c;
    // unsigned long l = (unsigned long) c;

    // int array[2];
    // int* x = array;
    // long* y = (long*) &(array[0]);

    // char* (*v)[3] = (char*(*)[3]) y;

    struct A a = {5, 0.5};
    struct B *b = (struct B*) &a;

    return 0;
}