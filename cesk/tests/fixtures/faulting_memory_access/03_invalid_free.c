#include <stdlib.h>

int main(){
    int * b = malloc(sizeof(int)*100);
    int * a = b+1;
    for(int i = 0; i < 99; i++){
        a[i] = -1;
    }
    free(a);
    return 0;
}
