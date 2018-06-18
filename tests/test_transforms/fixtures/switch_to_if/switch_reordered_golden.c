int main()
{
  {
    if (0 == 1)
    {
      goto censor01;
    }
    if (0 == 2)
    {
      goto censor03;
    }
    {
      goto censor02;
    }
  censor01:
    {
      goto censor04;
    }
  censor02:
    {
      goto censor04;
    }
  censor03:
    {
      goto censor04;
    }

  censor04:
  ;

  }
  {
    return 0;
  }
}
