struct one
{
  int a;
  long b;
  char c;
};

int main()
{
  struct one tester;
  *((int *) (((char *) (&tester)) + 0l));
  *((long *) (((char *) (&tester)) + 4l));
  *((char *) (((char *) (&tester)) + 8l));
  return 0;
}
