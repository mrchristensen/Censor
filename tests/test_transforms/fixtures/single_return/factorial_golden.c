int factorial(int x)
{
  int censor02;
  if (x == 0)
  {
    censor02 = 1;
    goto censor01;
  }
  else
  {

      censor02 = x * factorial(x - 1);
      goto censor01;

  }

  censor01:
  return censor02;

}

int main(int argc, char **argv)
{
  int censor04;
  if (argc < 2)
  {

      censor04 = 1;
      goto censor03;

  }

  int input = atoi(argv[1]);
  int output = factorial(input);

    censor04 = 0;
    goto censor03;

  censor03:
  return censor04;

}
