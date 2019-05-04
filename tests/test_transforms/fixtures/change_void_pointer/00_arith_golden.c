int main()
{
  int *x = 100;
  int *y = (int *) (((char *) x) + (20 * 2l));
  int diff = (((char *) y) - ((char*)x)) / 2l;
  x = (int *) (((char *) y) - (10 * 2l));
  y = (int *) ((10 * 2l) + ((char *) x));
  return 0;
}
