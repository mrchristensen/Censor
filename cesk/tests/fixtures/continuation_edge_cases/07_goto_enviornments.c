#include <stdio.h>

int main() {
    int i = 0;
    i = i;
    {
        int i = 4;
        a:
        i = i + 1;
        printf("%d\n",i); 
    } 
    if (i < 5){
        i = i + 1;
        goto a;
    } 
    return 0;
}
