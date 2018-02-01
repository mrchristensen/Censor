int main()
{
  int i = 0;
  int j = 0;
censor0:
  {
  i++;
  j = 0;
censor1:
  {
    j++;
    if (j < 10)
      goto censor1;

  }

  if (i < 10)
    goto censor0;

  }

}

