//for testing switch statements involves multiple cases, break, the keyword default

#include <stdio.h>

int main(){
    int j = 4;
    int sum = 0;
    
    while(j){
        switch(j){
            case 4:
                sum+=1000;
                break;
            case 2:
                sum+=200;
                sum*=10;
                break;
            case 1:
                sum+=290;    
            default:
                sum+=5;
        }
        j-=1;
    }

    printf("%d\n",sum);

    return 0;
}



