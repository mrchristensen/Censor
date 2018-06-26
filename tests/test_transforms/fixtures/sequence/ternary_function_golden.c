int f()
{
  return 0;
}

int main()
{
  int censor01;
  if (f())
  {
    censor01 = f();
  }
  else
  {
    censor01 = f();
  }
  int a = censor01;
  int censor02;
  if(0)
  {
    censor02 = f();
  }
  else
  {
    censor02 = f();
  }

  a = censor02;
  int censor03;
  if (1)
  {
    censor03 = f();
  }
  else
  {
    censor03 = f();
  }

  a = censor03;
  int censor04;
  if (f())
  {
    censor04 = 0;
  }
  else
  {
    censor04 = 0;
  }
  
  a = censor04;
  return 0;
}
