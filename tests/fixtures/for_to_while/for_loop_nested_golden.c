int main()
{
  int k = 0;
  {
    int i = 0
    while (i < 100)
    {
      k++;
      {
        int j = 0
        while (j < 100)
        {
          k++;
          j++;
        }

      }
      i++;
    }

  }
}

