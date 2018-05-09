#include <stdio.h>

struct one{
    int a;
    float b;
    long c;
    char d;
};

int main(){
    struct one two;
    struct one three;
    two.a = 1;
    two.b = 2.0;
    two.c = 3;
    two.d = '4';
    three = two;
    
    printf("%d\n",two.a);
    printf("%f\n",two.b);
    printf("%ld\n",three.c);
    printf("%c\n",three.d);

    return 0;

}
