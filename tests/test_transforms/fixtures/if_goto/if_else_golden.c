int main()
{
  int i = 0;
  if (true)
  {
      i = 10;
      goto censor01_ENDIF;
  }
  {
    i = 20;
  }
censor01_ENDIF:
  (void ) 0;

  return 0;
}
