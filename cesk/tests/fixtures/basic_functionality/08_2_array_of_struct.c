#include <stdio.h>

struct my_struct{
    int a;
    int b;
};

int main(){
    struct my_struct test[3];
    
    test[2].a = 100;

    printf("%d\n",test[2].a);   

    return 0;
}
