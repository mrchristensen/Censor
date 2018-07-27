#include <stdio.h>

struct ints{
    int x;
    int y;
    int z;
};

int get_offset(int* first, int* second){
    return second - first;
}

int main(){
    struct ints first = {1,2,3};
    struct ints second;
    second.z = 1234;
    int* a = (int*)&first;
    int* b = (int*)&(first.z);
    int offset = get_offset(a,b);
    int* c = ((int*)&second)+offset;
    printf("%d\n",*c);
    return 0;        
}

