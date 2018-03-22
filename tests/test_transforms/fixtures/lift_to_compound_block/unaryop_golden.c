int main()
{
  int a[5];
  int i = 0;
  LOOP:
  {
    i++;
    int *censor01 = &a[i];
    *censor01 = 0;
    int censor02 = i < 4;
    if (censor02)
      goto LOOP;
  }
}
