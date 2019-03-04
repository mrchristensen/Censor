#include <stdio.h>
enum myEnums;
enum myEnums {
    zero,
    one,
    two = one,
    one_again = 1 + zero,
    two_again,
};

enum {
    other_zero = zero
};

enum myEnums foo(enum myEnums b){
    return b;
}

int main(){
    enum myEnums a = one;
    int i = zero;
    printf("%d %d %d %d %d\n",zero + other_zero, one, two, one_again, two_again);
}
