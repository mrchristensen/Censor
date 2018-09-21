struct one
{
  int a;
  long b;
  char c;
};

int main()
{
  struct one tester;
  *((int *) (((void *) (&tester)) + 0l));
  *((long *) (((void *) (&tester)) + 4l));
  *((char *) (((void *) (&tester)) + 8l));
  return 0;
}
