#include <stdio.h>
int main(){
    int i = 0x00636261;
    char* c = (char*)&i;
    printf("%s\n",c);
}