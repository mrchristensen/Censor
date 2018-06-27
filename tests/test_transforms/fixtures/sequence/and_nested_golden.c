int main()
{
  int censor02 = 0;
  if (5)
  {
    censor02 = 2 != 0;
  }

  int censor01 = 0;
  if (censor02)
  {
    censor01 = 6 != 0;
  }
  
  int a = censor01;
  int censor03 = 0;
  if (5)
  {
    int censor04 = 0;
    if (2)
    {
      censor04 = 6 != 0;
    }
    
    censor03 = censor04 != 0;
  }

  int b = censor03;
  return 0;
}