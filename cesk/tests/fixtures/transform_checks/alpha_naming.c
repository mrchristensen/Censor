#include <stdio.h>

struct array_struct
{
    int a[2];
    char buf[10];
};

int i = 10;
int p(int i)
{
    {
        int i = 9;
        i++;
    }
    printf("%d", i);
    return i;
}

int test(int i, int j, int k)
{
    {
        int i = j;
        int k = i;
        k++;
        j = k;
    }
    i = j;
    k = j;
    {
        int j = i;
        j++;
        j--;
        p(k);
        {
            k++;
            int j = k;
            int k = i;
            k++;
            p(k);
        }
        p(k);
    }
    p(p(i));
    return 0;
}

int main()
{
    int i = 0;
    p(i);
    {
        int i = 1;
        p(i);
        {
            int i = 2;
            p(i);
            {
                int i = 3;
                p(i);
                {
                    int i = 4;
                    p(i);
                }
                p(i);
            }
            p(i);
        }
        p(i);
    }
    p(i);
    {
        int i = 5;
        {
            int i = 6;
            {
                int i = 7;
                {
                    int i = 8;
                    p(i);
                }
                p(i);
            }
            p(i);
        }
        p(i);
    }
    p(i);
    test(0, 5, 0);
}
