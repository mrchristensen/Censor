int main()
{
  int* x = 100;
  int* y = x + 20;
  int diff = y - x;
  x = y - 10;
  y = 10 + x;
  return 0;
}
