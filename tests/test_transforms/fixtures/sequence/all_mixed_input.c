int f(int a, int b, int c)
{
  return 0;
}
int main()
{
  int a = 0;
  int b = 0;
  int c = 0;
  int d = (a = a+1, c || f(a && a, 0, (b = b + 30,c)? b * a:b + a));
  return 0;
}