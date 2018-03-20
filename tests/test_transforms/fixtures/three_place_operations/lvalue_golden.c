int main()
{
  int a[10];
  int *p = &a[0];
  int censor03 = 9 + 3;
  int censor02 = 4 / 2;
  int *censor01 = p + censor02;
  *censor01 = censor03 - 4;
}
