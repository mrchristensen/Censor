int global[10] = {1, 2, 3, 4, 5, 6};
void censor01_INIT_GLOBALS();
int main()
{
  censor01_INIT_GLOBALS();
  int a[10] = {1, 2, 3, 4, 5, 6};
  int b[10] = {1, [4] = 5, 6, 7, [2] = 2};
  int c[10][10] = {{1, 2, 3}, {4, 5, 6}};
  int d[10][10] = {[2] = {1, 2, 3}, {4, 5, 6}};
  int e[10][10] = {1, 2, 3, 4, 5};
  int f[] = {1, 2, 3, 4, 5, 6};
  int g[][3] = {1, 2, 3, 4, 5, 6};
}

void censor01_INIT_GLOBALS()
{
  global[0] = 1;
  global[1] = 2;
  global[2] = 3;
  global[3] = 4;
  global[4] = 5;
  global[5] = 6;
}
