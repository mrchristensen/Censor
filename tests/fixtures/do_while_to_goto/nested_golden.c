int main()
{
  int i = 0;
  int j = 0;
$1:
  {
  i++;
  j = 0;
$2:
  {
    j++;
    if (j < 10)
      goto $2;

  }

  if (i < 10)
    goto $1;

  }

}

