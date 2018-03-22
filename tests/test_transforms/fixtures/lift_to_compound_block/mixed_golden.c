
struct rects
{
  int x[10];
  int y[10];
};
int main()
{
  struct rects *r = (struct rects *) malloc(sizeof(r));
  int i = 0;
  int t = 0;
 OUTER:
  {
    int j = 0;
  INNER:
    {
      int (*censor01)[10] = &r->x;
      i = i + 1;
      int *censor02 = &(*censor01)[i];
      int censor03 = t + (*censor02);
      int (*censor04)[10] = &r->y;
      j = j + 1;
      int *censor05 = &(*censor04)[j];
      t = censor03 + (*censor05);
      int censor06 = j < 10;
      if (censor06)
        goto INNER;

      i++;
      int censor07 = i < 10;
      if (censor07)
        goto OUTER;

    }

  }

}
