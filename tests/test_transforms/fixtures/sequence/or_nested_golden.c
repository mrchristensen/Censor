int main()
{
  int censor02 = 1;
  if (5 == 0)
  {
    censor02 = 2 != 0;
  }

  int censor01 = 1;
  if (censor02 == 0)
  {
    censor01 = 6 != 0;
  }

  int a = censor01;
  int censor03 = 1;
  if (5 == 0)
  {
    int censor04 = 1;
    if (2 == 0)
    {
      censor04 = 6 != 0;
    }
    
    censor03 = censor04 != 0;
  }

  int b = censor03;
  return 0;
}
