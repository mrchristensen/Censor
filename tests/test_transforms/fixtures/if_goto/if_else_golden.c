int main()
{
  int i = 0;
  if (true)
  {
      i = 10;
      goto censor01;
  }
  {
    i = 20;
  }
censor01:
  return 0;
}
