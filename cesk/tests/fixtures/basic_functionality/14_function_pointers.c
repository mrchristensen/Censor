#include <stdio.h>

void foo(int n){
    printf("foo %d\n",n);
}
void bar(int n){
    printf("bar %d\n",n);
}
void invokeDouble(void (*function)(int),int n){
    function(n*2);
}
int main(){
    void (*function_pointer)(int);
    function_pointer = foo;
    function_pointer(100);
    function_pointer = bar;
    function_pointer(200);

    int size = 10;
    void (*fun_ptr[size])(int);
    for (int i = 0; i < size; i++){
        if (i % 2){
            fun_ptr[i] = foo;
        }
        else
        {
            fun_ptr[i] = bar;
        }   
    }
    
    for (int j = 0; j < size; j++){
        fun_ptr[j](j);
    }

    for (int k = 0; k < size; k++){
        invokeDouble(fun_ptr[k],k);
    }
}
