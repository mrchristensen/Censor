int a[10];
void censor01_INIT_GLOBALS();
int main()
{
  censor01_INIT_GLOBALS();
  int s[10] = {1, 2, 3};
}

int b[10];
void censor01_INIT_GLOBALS()
{
  a[0] = 1;
  a[1] = 2;
  a[2] = 3;
  a[3] = 4;
  a[4] = 5;
  a[5] = 6;
  b[0] = -1;
  b[1] = -2;
  b[2] = -3;
  b[3] = -4;
  b[4] = 3 * 2;
}

