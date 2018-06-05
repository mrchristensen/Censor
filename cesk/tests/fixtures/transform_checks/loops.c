#include <stdio.h>

int main(){
    int j = 9;
    int sum = 0;
    do{
        sum+=j;
        j-=1;
    }while(j>5);

    for(int i = 0; i<j; i+=1){
        sum*=7;
        sum+=j;
    }

    printf("%d\n",sum);
    ;;;;;;;;;;;;;;;;;
    return 0;
}
