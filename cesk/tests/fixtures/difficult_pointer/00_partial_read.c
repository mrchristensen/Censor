#include <stdio.h>

int main(){
    long l = 0x3132333435363738;

    char* ptr = (char*) &l;

    for(int i = 0; i < 8; i++,ptr++)
        printf("%c ",(char)*(ptr));

    return 0;
}
