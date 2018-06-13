int main()
{
  int *x = 100;
  int *y = (int *) (((void *) x) + (20 * 2));
  int diff = (((void *) y) - ((void*)x)) / 2;
  x = (int *) (((void *) y) - (10 * 2));
  y = (int *) ((10 * 2) + ((void *) x));
  return 0;
}
