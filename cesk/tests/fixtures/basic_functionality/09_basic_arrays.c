#include <stdio.h>

int main() {
    int a[10] = {2,1,1,1,1,1,1,1,1,1};
    int sum = 0;
    int i = 0;
    
    loop:;
		sum = sum + a[i];
		i = i + 1;
                printf("%d   ",i);
                printf("%d\n",sum);
	if (i < 10) {
		goto loop;
	}
    
    return 0;
}
