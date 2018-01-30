int main()
{
  int j = 0;
  {
    int i = 0;
    while (i < 10)
    {
      while (j < 10)
      {
        j++;
        if ((j % 2) == 0)
          continue;

        j++;
      }

      j = 0;
      i++;
    }

  }
}

