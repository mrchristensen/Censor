int main()
{
  int i = 0;
  int j = 0;
censor04:
  {
    i++;
    j = 0;
  censor02:
    {
      j++;
      censor01:
      {
      if (j < 10)
        goto censor02;

      }

    }

    censor03:
    {
    if (i < 10)
      goto censor04;

    }

  }

}
