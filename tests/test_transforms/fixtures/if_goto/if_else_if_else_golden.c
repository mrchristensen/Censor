int main()
{
  int i = 0;
  if (true)
  {
      i = 10;
      goto censor02_ENDIF;
  }

  {
    if (true)
    {
        i = 20;
        goto censor01_ENDIF;
    }

    {
      i = 30;
    }
    censor01_ENDIF:
      (void ) 0;


  }
  censor02_ENDIF:
    (void ) 0;


  return 0;
}
