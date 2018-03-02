int main()
{
  int i = 4;
  {
    float i = 7.3;
    {
      float *censor01 = &i;
      *censor01 = (*censor01) + 3;
    }
  }
}
