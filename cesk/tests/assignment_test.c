#include <stdio.h>

int main(){
    int a[2] = {1,2};
    int i = 0;
    int sum = 0;

    loop:

        sum = sum + a[i];
        i = i + 1;
        if(i<2)
            goto loop;

 
    printf("%d\n",sum); 

    return 0;
}
