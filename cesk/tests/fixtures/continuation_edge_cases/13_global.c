#include <stdio.h>

int x = 45;

struct l{
    int x;
    char y;
};

struct l * ptr = 0;
struct l item = {4,'5'};
//char* error_msg = "Hello World\n";
int arr[5] = {1,2,3,4,5};

int main(){
    printf("%d\n",x);
    printf("%ld\n",(long)ptr);
    printf("%d\n",item.x);
    printf("%d\n",arr[4]);
    return 0;
}
