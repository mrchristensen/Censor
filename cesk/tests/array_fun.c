#include <stdio.h>

int main(){
    int arr[2][2][2][2] = { { {{1,2},{3,4}}, {{5,6},{7,8}} } , { {{9,10},{11,12}}, {{13,14},{15,16}} } } ;
    int* ptr = (int*) arr[0][1];
    printf("%d",*ptr);
    return 0;
}
