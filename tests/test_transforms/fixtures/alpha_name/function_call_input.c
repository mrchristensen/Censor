int main(){
    int i = 3;
    {
        int i = 0;
        return f(i);
    }
}
int f(int i){
    {
        int i = 0;
    }
    return i;
}
int j(){
  return 0;
}