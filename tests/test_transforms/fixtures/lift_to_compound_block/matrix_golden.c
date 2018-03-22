int main()
{
  int matrix[3][3] = {{1, 2, 3}, {1, 2, 3}, {1, 2, 3}};
  int t = 0;
  int i = 0;
  int j = 0;
 OUTER:
  {
    j = 0;
  INNER:
    {
      int (*censor01)[3] = &matrix[i];
      int *censor02 = &(*censor01)[j];
      t = t + (*censor02);
      j++;
      int censor03 = j < 10;
      if (censor03)
        goto INNER;

      i++;
      int censor04 = i < 10;
      if (censor04)
        goto OUTER;

    }

  }

}
