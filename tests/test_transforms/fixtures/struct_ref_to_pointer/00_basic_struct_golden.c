struct one
{
  int a;
  long b;
  char c;
};

int main()
{
  struct one tester;
  *((int *) (((void *) (&tester)) + 0));
  *((long *) (((void *) (&tester)) + 4));
  *((char *) (((void *) (&tester)) + 8));
  return 0;
}
