int main()
{
  int i = 0;
  do
  {
    i++;
    goto censor01;
  }
  while (i);
  censor01:
  ;

  return 0;
}
