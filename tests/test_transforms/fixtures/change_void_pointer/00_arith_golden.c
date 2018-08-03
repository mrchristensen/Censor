int main()
{
  int *x = 100;
  int *y = (int *) (((void *) x) + (20 * 2l));
  int diff = (((void *) y) - ((void*)x)) / 2l;
  x = (int *) (((void *) y) - (10 * 2l));
  y = (int *) ((10 * 2l) + ((void *) x));
  return 0;
}
