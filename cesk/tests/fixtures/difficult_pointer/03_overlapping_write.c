#include <stdio.h>

int main(){

char arr[100];

int* ints = (int*) arr;

for( int i = 0; i < 25; i++)
    ints[i] = i;


for( int i = 0; i < 25; i+=4)
    printf("%d ",(int)arr[i]);

return 0;

}
