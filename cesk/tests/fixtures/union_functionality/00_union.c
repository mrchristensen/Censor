#include <stdio.h>

union test { 
    int x; 
    int y; 
}; 
  
int main() 
{ 
    union test p1; 
    p1.x = 65; 
    p1.y = 34;
  
    // p2 is a pointer to union p1 
    union test* p2 = &p1; 
  
    // Accessing union members using pointer 
    printf("%d", p2->x);
    printf("%d %d", p2->x, p2->y); 
    return 0; 
} 