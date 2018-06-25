int f(int x, int y, int z){}
int main(){
    int a = 2;
    int b = 3;
    b, b && b || b;
    a = (b = 35, f((a,b) && a, 0, b) || 1)?b:a&&b;
    return 0;
}
