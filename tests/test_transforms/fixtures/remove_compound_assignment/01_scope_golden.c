int main()
{
  int i = 4;
  {
    float i = 7.3;
    {
      float *$2 = &i;
      *$2 = (*$2) + 3;
    }
  }
}
