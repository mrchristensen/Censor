int main()
{
  int i = 0;
  if (true)
  {
      i = 10;
      goto censor02;
  }

  {
    if (true)
    {
        i = 20;
        goto censor01;
    }

    {
      i = 30;
    }
    censor01:


  }
  censor02:


  return 0;
}
