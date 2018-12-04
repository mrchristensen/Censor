int main()
{
  #pragma omp parallel
  {
    {
      int i = 0;
      #pragma omp for
for (i = 0; i < 10; ++i)
      {
      }

    }
    {
      int i = 0;
      int censor01 = 10;
      #pragma omp for
for (i = 0; i < 10; i = i + censor01)
      {
      }

    }
  }
}

