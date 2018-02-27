int main()
{
  int a = 0;
  {
    int *$1 = &a;
    *$1 = (*$1) + 1;
  }
}
 