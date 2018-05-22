int main() {
    // char c = 5;
    // short s = (short) c;
    // int i = (int) c;
    // unsigned long l = (unsigned long) c;

    int array[2];
    // int* x = array;
    long* y = (long*) &(array[0]);

    char* (*v)[3] = (char*(*)[3]) y;

    return 0;
}