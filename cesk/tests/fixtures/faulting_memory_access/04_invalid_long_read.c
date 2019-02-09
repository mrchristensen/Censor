int main(){
    int a = 3;
    int b = 5;
    int c = 4;
    long* l = (long*)&b;
    return *l * 0;
}