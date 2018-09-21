#include <stdio.h>

struct ints{
    int x;
    int y;
    int z;
};

int main(){
    struct ints first = {1,2,3};
    struct ints second;
    second.x = 1234;
    int* a = (int*)&first;
    int* b = (int*)&(first.z);
    int offset = b - a;
    int* c = ((int*)&second.z)-offset;
    printf("%d\n",*c);
    return 0;        
}
