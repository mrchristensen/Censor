int f(int a, int b, int c)
{
  return 0;
}
int main()
{
  int a = 0;
  int b = 0;
  int censor01 = a + 1;
  int censor02 = f(a, censor01, b);
  int censor03 = f(0, 0, 0) * b;
  int c = f(censor02, 0, censor03);
  return 0;
}