int main()
{
  {
    int i = 0
    while (i < 10)
    {
      {
        int j = 0
        while (j < 10)
        {
          if ((j % 2) == 0)
          {
            {
              j++;
              continue;
            }
          }

          {
            j++;
            continue;
          }
          j++;
        }

      }
      i++;
    }

  }
}

