#include <stdio.h>

int main(){
    char  c[4] = {1,2,3,4};

    int* ptr = (int*) c;

    printf("%d\n",*ptr);

    return 0;
}
