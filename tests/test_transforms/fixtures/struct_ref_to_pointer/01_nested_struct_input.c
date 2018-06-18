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
  tester->c.c;
  tester->d;
  return 0;
}
