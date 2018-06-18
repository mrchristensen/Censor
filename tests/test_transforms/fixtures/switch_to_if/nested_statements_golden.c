int main()
{
  {
    if (0 == 1)
    {
      goto censor03;
    }
    if (0 == 2)
    {
      goto censor04;
    }
    if (0 == 3)
    {
      goto censor05;
    }
    {
      goto censor06;
    }
  censor03:
    {
      while(1)
      {
        {
          {
            goto censor01;
          }
          censor01:
          {
            goto censor02;
          }

          censor02:
          ;

        }
      }

    }
  censor04:
    {
      for (;;)
        break;

    }
  censor05:
    {
      do
      {
        break;
      }
      while(1);
    }
  censor06:
  ;

  }
  {
    return 0;
  }
}
