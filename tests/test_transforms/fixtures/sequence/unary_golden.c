void f(int a, int b, int c, int d, int e)
{
}

int main()
{
  int a = 0;
  int censor01 = *(&a);
  int censor02 = a++;
  f(3, 5, a, censor01, censor02);
}

