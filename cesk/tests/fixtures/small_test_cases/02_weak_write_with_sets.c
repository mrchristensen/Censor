#include <stdio.h>

int socket_cb(){
    int j = 1;

    mocked_function(j);

    if(j == 0){
        j=100;
    }
    if (j == 1){
        j=101;
    }
    else if (j == 2){
        j = 102;
    }
    
    printf("%d", j);
    return 0;
}
