#include <stdio.h>
void test_p(int p)
{
    if (p)
        printf(".");
    else
        printf("Failed p\n");
    if (!p)
        printf("Failed !p\n");
    else
        printf(".");
    if (p + p)
        printf(".");
    else
        printf("Failed p + p\n");
}
void test_n(int n)
{
    if (n)
        printf(".");
    else
        printf("Failed n\n");
    if (!n)
        printf("Failed !n\n");
    else
        printf(".");
    if (n + n)
        printf(".");
    else
        printf("Failed n + n\n");
}
void test_z(int z)
{
    if (z)
        printf("Failed z\n");
    else
        printf(".");
    if (!z)
        printf(".");
    else
        printf("Failed !z\n");
    if (z == z)
        printf(".");
    else
        printf("Failed z == z\n");
}
void test_b_n(int b, int n)
{
    if (n < b)
        printf(".");
    else
        printf("Failed n < b\n");
    if (b > n)
        printf(".");
    else
        printf("Failed b > n\n");
    if (n <= b)
        printf(".");
    else
        printf("Failed n <= b\n");
    if (b >= n)
        printf(".");
    else
        printf("Failed b >= n\n");
    if (b == n)
        printf("Failed b == n\n");
    else
        printf(".");
    if (b != n)
        printf(".");
    else
        printf("Failed b != n\n");
}
void test_nb_p(int nb, int p)
{
    if (p > nb)
        printf(".");
    else
        printf("Failed p > nb\n");
    if (nb < p)
        printf(".");
    else
        printf("Failed nb < p\n");
    if (nb <= p)
        printf(".");
    else
        printf("Failed nb <= p\n");
    if (p >= nb)
        printf(".");
    else
        printf("Failed p >= nb\n");
    if (nb == p)
        printf("Failed nb == p\n");
    else
        printf(".");
    if (nb != p)
        printf(".");
    else
        printf("Failed nb != p\n");
}
void test_b_nb(int b, int nb){
    if (nb > b)
        printf("Failed nb > b\n");
    else
        printf(".");
    if (b < nb)
        printf("Failed b < nb\n");
    else
        printf(".");
}

int main()
{
    int p = 1;      //  +    (p)ositive
    int n = -1;     //  -    (n)egative
    int z = 0;      //  0    (z)ero
    int b = p == p; //  0+   (b)oolean
    int nb = -b;    // -0    (n)egative (b)oolean
    int t = b + nb; // -0+   (t)op

    test_p(p);
    test_n(n);
    test_z(z);
    test_b_n(b, n);
    test_nb_p(nb, p);
    test_b_nb(b, nb);

    printf("\n");
}