int main()
{
  int n;
  int first = 0;
  int second = 1;
  int next;
  int c;
  n = 30;
  {
    c = 0;
    int censor11 = c < n;
    if (censor11)
      censor02:
    {
      int censor12 = c <= 1;
      if (censor12)
      {
        next = c;
        goto censor01_ENDIF;
      }

      {
        next = first + second;
        first = second;
        second = next;
      }
      censor01_ENDIF:
      

      printf("%d\n", next);
      c++;
      int censor13 = c < n;
      if (censor13)
        goto censor02;

    }


  }
  return 0;
}

