int main()
{
  int a = 0;
  int b = 0;
  int c = 0;
  int censor02;
  if (a > (b + c))
  {
    censor02 = a;
  }
  else
  {
    int censor03;
    if (b)
    {
      censor03 = b;
    }
    else
    {
      censor03 = c;
    }
    censor02 = censor03;
  }

  int censor01;
  if (censor02)
  {
    int censor04;
    if (a)
    {
      censor04 = a;
    }
    else
    {
      censor04 = b;
    }

    censor01 = censor04;
  }
  else
  {
    int censor05;
    if ((c - b) == 2)
    {
      censor05 = c - b;
    }
    else
    {
      censor05 = c + b;
    }

    censor01 = censor05;
  }
  
  a = censor01;
}
