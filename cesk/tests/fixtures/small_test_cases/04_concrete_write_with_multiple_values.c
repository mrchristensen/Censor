#include <stdio.h>

int socket_cb(){
    int j = -1;

    j = mocked_function(j);

    if(j == 0){
        j=100;
    }
    else  if (j == 2){
         j = mocked_function(j);
         if(j=2){
             j = 103;
         }
    }
    else if (j == 4){
        j = 102;
    }
    
    printf("%d", j);
    return 0;
}
