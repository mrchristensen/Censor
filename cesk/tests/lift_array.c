#include <stdio.h>

int main(){
    int array[3][3];
       
    array[0+1][1+1] = 100;

    int* ptr2 = array[1+0];
    
    int temp = ptr2[2];
    int add = 10 + temp;

    printf("%d\n",add);

    return 0;

}
