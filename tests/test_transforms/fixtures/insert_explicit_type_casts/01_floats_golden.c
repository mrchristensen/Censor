int main()
{
  float a = (float) 0;
  double b = (double) 0;
  long double c = (long double) 0;
  a = (float) (((long double) b) + c);
  b = (double) (((long double) a) + c);
  c = (long double) (b + ((double) a));
  a = a + a;
  a = (float) (((long double) (((double) a) + b)) + (c + ((long double) a)));

  int i;
  i = (int) (((float) i) + a);
  i = (int) (b + ((double) i));
  i = (int) (((long double) i) + c);

  float f = (float) (((double) 1) + 0.0);
  f = ((float) 1) + 0.0f;
  f = ((float) 1) + 0.0F;
  f = (float) (((long double) 1) + 0.0l);
  f = (float) (((long double) 1) + 0.0L);

}
