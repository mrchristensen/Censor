#include <stdio.h>

struct innermost{
    double a;
    char b;
};

struct my_struct{
    char a;
    int b;
    struct innermost c;   
};

struct one{
    int a;
    float b;
    long c;
    struct my_struct d;
};



int main(){
    //fun to test nested init lists, but this is not implemented yet
    //struct one tester = {1,2.0,3,{'4',5,{6.0,'7'}}};

    //so for now
    struct one tester = {1,2.0,3};
    tester.d.a = '4';
    tester.d.b = 5;
    tester.d.c.a = 6.0;
    tester.d.c.b = '7';
       
    printf("%d\n",tester.a);
    printf("%c\n",tester.d.a);
    printf("%f\n",tester.d.c.a);
       
    return 0;
}
