int main()
{
  float a = (float) 0;
  double b = (double) 0;
  long double c = (long double) 0;
  a = (float) (((long double) b) + c);
  b = (double) (((long double) a) + c);
  c = (long double) (b + ((double) a));
  a = (float) (a + a);
  a = (float) (((long double) (((double) a) + b)) + (c + ((long double) a)));

  int i;
  i = (int) (((float) i) + a);
  i = (int) (b + ((double) i));
  i = (int) (((long double) i) + c);
}
