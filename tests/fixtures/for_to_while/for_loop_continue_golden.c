int main()
{
  int j = 0;
  {
    int i = 0
    while (i < 10)
    {
      if ((i % 2) == 0)
      {
        i++;
        continue;
      }

      j++;
      {
        i++;
        continue;
      }
      j--;
      i++;
    }

  }
}

