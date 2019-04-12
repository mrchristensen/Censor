#include <stdio.h>
int f(int* x){
    *x = 4;
}
int ary[5];
int main(){
    ary[2] = 3;
    f(&ary[2]);
    printf("%d\n", ary[2]);
}