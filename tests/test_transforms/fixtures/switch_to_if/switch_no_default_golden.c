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
      goto censor03;
    }
  censor02:
    {
      goto censor03;
    }
  censor03:
  ;

  }
  {
    return 0;
  }
}
