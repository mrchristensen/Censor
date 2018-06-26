int f(int a, int b, int c)
{
  return 0;
}
int main()
{
  int a = 0;
  int b = 0;
  int c = 0;
  a = a + 1;
  int censor01 = 1;
  if (c == 0)
  {
    int censor02 = 0;
    if (a)
    {
      censor02 = a != 0;
    }

    b = b + 30;
    int censor03;
    if (c)
    {
      censor03 = b * a;
    }
    else
    {
      censor03 = b + a;
    }

    censor01 = f(censor02, 0 , censor03) != 0;
  }
  int d = censor01;
  return 0;
}