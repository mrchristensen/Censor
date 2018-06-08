int main()
{
  {
    if (0 == 1)
    {
      goto censor01;
    }
    if (0 == 2)
    {
      goto censor02;
    }
    {
      goto censor03;
    }
  censor01:
    {
    }
  censor02:
    {
    }
  censor03:
    {
      ;
    }
  censor04:


  }
  {
    return 0;
  }
}