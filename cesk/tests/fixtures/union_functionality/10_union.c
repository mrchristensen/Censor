#include <stdio.h>
//Write to an int and print the double

union test { 
    int x; 
    double y; 
}; 

int main() 
{ 
    union test p1; 
    p1.x = 65;

    printf("%f %d", p1.y, p1.x); 
    return 0; 
}