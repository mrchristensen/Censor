struct one
{
    int a;
    long b;
    char c;
};

struct two
{
  char a;
  char b;
  struct one c;
  long d;
};

int main()
{
  struct two *tester;
  *((char *) (((void *) (&(*((struct one *) (((void *) tester) + 4))))) + 8));
  *((long *) (((void *) tester) + 16));
  return 0;
}
