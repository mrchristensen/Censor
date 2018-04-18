#include <stdio.h>
int main() {
    int i[5];
    int temp2 = i[3];

    i[3] = 5;
    temp2 = i[3];
    printf("%d\n",temp2);

    i[0] = 1;
    temp2 = *i;
    printf("%d\n",temp2);

    int j[5][5];
    j[1][2] = 3;
    temp2 = j[1][2];
    printf("%d\n",temp2);
    
    return 0;
}
