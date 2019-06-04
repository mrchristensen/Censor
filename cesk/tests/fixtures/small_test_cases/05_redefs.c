#include <stdio.h>

//Two typedefs of structs, where both include a name thingy at the bottem make 12 redefinitions appear
typedef struct testOne {
    int test;
} testTestOne;

typedef struct testTwo {
    int test;
} testTestTwo;

int socket_cb(){
    return 0;
}