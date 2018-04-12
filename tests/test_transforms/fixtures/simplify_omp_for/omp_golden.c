int main()
{
  #pragma omp parallel
  {
    {
      int i = 0;
      int censor01 = 10;
      #pragma omp for
for (i = 0; i < censor01; ++i)
      {
      }

    }
    {
      int i = 0;
      int censor02 = 10;
      int censor03 = 10;
      #pragma omp for
for (i = 0; i < censor02; i = i + censor03)
      {
      }

    }
  }
}

