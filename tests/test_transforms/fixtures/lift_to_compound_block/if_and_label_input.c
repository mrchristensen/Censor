int printf(const char * __format, ...);
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
    if (c < n)
      censor02:
    {
      if (c <= 1)
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
      (void)(0);


      if (printf("%d\n", next))
      {
        c++;
      }
      if (c < n)
        goto censor02;

    }


  }
  return 0;
}

