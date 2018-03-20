int main()
{
    int a[10];
    int *p = &a[0];

    *(p + 4 / 2) = 9 + 3 - 4;

}