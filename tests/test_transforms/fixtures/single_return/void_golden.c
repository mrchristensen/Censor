void otherStuff()
{
  goto censor01;
  censor01:
  return;

}

void differentOtherStuff()
{
  goto censor02;
  censor02:
  return;

}

void doStuff(int x)
{
  if (x > 1)
  {
    otherStuff();
    goto censor03;
  }
  else
    if (x < (-1))
  {
    differentOtherStuff();
    goto censor03;
  }
  else
  {
    goto censor03;
  }


  censor03:
  return;

}
