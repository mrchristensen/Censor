int f(int a, int b, int c)
{
  return 0;
}
int main()
{
  int a = 0;
  int b = 0;
  int c = f(f(a,a+1,b),0,f(0,0,0) * b);
  return 0;
}