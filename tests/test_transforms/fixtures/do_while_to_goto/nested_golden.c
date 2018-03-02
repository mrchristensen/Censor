int main()
{
  int i = 0;
  int j = 0;
censor01:
  {
  i++;
  j = 0;
censor02:
  {
    j++;
    if (j < 10)
      goto censor02;

  }

  if (i < 10)
    goto censor01;

  }

}

