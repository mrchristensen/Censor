int main()
{
  int a = 0;
  {
    int *censor01 = &a;
    *censor01 = (*censor01) + 1;
  }
}
