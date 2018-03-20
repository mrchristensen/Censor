int main() {
  int matrix[3][3] = {
    {1,2,3},
    {1,2,3},
    {1,2,3},
  };

  int t = 0;
  int i = 0;
  int j = 0;
 OUTER:
  {
    j = 0;
  INNER:
    {
      t = t + matrix[i][j];
      j++;
      if (j < 10)
        goto INNER;
      i++;
      if (i < 10)
        goto OUTER;
    }
  }
}
