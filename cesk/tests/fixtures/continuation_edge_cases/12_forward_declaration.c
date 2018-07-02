#include <stdio.h>

int my_func(int x);

int main(){
    int y = my_func(2);
    printf("%d\n",y);
    return 0;       
}

int my_func(int x){
    return x*3;
}
