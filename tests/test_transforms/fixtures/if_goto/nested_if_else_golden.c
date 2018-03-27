int main()
{
  int i = 0;
  if (true)
  {
    i = 10;
    if (true)
    {
        i = 20;
        goto censor01;
    }

    i = 30;
    censor01:

    goto censor03;
  }

  i = 40;
  if (true)
  {
      i = 50;
      goto censor02;
  }

  i = 60;
  censor02:


  censor03:

  return 0;
}
