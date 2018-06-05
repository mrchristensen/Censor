#include <stdio.h>

int main(){

    int j = 9;
    int sum = 0;

    while(j){
        if(j==5)
            break;
        sum += j;
        j-=1;
    }

    printf("%d\n",sum);

}
