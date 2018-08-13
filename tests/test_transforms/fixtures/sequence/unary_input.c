void f(int a, int b, int c, int d, int e){

}
int main(){
    int a = 0;
    f(3,5,a,*(&a),a++);
}