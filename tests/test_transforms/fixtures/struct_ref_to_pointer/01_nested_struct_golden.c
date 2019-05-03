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
  *((char *) (((char *) (&(*((struct one *) (((char *) tester) + 4l))))) + 8l));
  *((long *) (((char *) tester) + 16l));
  return 0;
}
