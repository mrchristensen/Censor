int main()
{
  int a[5];
  int i = 0;
  i = i;
  i++;
  LOOP:
  {
    a[i] = 0;
    i++;
    int censor01 = i < 4;
    if (censor01)
      goto LOOP;
  }
}
