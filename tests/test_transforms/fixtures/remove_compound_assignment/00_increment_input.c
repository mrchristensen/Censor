int main() {
    int a = 0;
    a += 1;

    int arr[8] = {1,2,3,4,5,6};
    arr[1] += 1;

    int *p = arr;
    p += 1;

    *p += 1;

    int **p2 = arr;
    **p2 += 1;

    *&a += 1;

    *(p + 3) += 1;

    long int b;
    b += 1;

    *(p + b) += 1;

}
