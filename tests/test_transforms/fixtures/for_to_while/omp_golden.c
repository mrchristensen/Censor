int main()
{
  #pragma omp parallel
  {
    #pragma omp for
    for (int i = 0; i < 10; ++i)
    {
      {
        int j = 0;
        while (j < 10)
        {
          ++j;
        }

      }
    }

    #pragma omp for
    for (int i = 0; i < 10; ++i)
    {
    }

  }
}

