#include <stdio.h>

int main(){
    int x = 5;
    int* y = &x;
    y = y + 1;
    y = y - 1;
    printf("%d\n",*y);
    return 0;        
}

