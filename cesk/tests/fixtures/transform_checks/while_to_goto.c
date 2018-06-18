

#include <stdio.h>

int main(){
    int j = 10;
    int sum = 0;
{
    j = 9;
    *&j = (*&j) + 1;
}
    while(j){
        j -= 1;
        sum += j;    
        printf("%d\n",sum);
    }

    printf("%d\n",sum);
    return 0;
}
/*
TRANSFORMED TO

int main(){
    int censor06;

    int j = 10;
    int sum = 0;

    if(j)
      censor01:
      {
        int *censor02 = (int*) &j;
        *censor02 = (*censor02) - 1;
        
        int *censor03 = (int*) &sum;
        (*censor03) = (*censor03) + j;

        if(j)
            goto censor01;
      }

    printf((const char *)"%d\n",sum);
    censor06 = 0;
    goto censor05;

    censor05:
    return censor06;
*/
