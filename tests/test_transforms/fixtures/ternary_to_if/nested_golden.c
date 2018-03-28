int main()
{
  int a = 0;
  int b = 0;
  int c = 0;
  int censor01;
  if (b)
    censor01 = b;
  else
    censor01 = c;

  int censor02;
  if (a > (b + c))
    censor02 = a;
  else
    censor02 = censor01;

  int censor03;
  if (a)
    censor03 = a;
  else
    censor03 = b;

  int censor04;
  if ((c - b) == 2)
    censor04 = c - b;
  else
    censor04 = c + b;

  int censor05;
  if (censor02)
    censor05 = censor03;
  else
    censor05 = censor04;
  a = censor05;
}
