int f(){
    return 0;
}
int main(){
    int a = f()?f():f();
    a = 0?f():f();
    a = 1?f():f();
    a = f()?0:0;
    return 0;
}