#include <stdio.h>
#define num_ints 55

int sum(int arr[num_ints]){
    int sumt = 0;
    for(int i = 0; i < num_ints; i++){
        sumt += arr[i];
    }
    arr[0] = 100;
    return sumt;
}

int main(){
    int arr[num_ints];
    for(int i = 0; i < num_ints; i++){
        arr[i] = i;
    }
    int x = sum(arr);
    printf("%d\n",x);
    printf("%d\n",arr[0]);
    return 0;
}
