#include <stdio.h>
    
int main(){
	int i = 9;
	float f = 4.2;
	float itof = (float)i+f;
	int i_implicit = f+i;
	float f_implicit = i+f;
	int ftoi = i + (int) f;
	
	printf("i_implicit %d\n",i_implicit);
 	printf("f_implicit %f\n",f_implicit);
	printf("int->float: %f\n",itof);
	printf("float->int: %d\n",ftoi);

	return 0;
}

