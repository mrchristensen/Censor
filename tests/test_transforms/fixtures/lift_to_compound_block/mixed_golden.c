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
      int censor02 = i + 1;
      i = censor02;
      int *censor03 = &(*censor01)[i];
      int censor04 = t + (*censor03);
      int (*censor05)[10] = &r->y;
      int censor06 = j + 1;
      j = censor06;
      int *censor07 = &(*censor05)[j];
      int censor08 = censor04 + (*censor07);
      t = censor08;
      int censor09 = j < 10;
      if (censor09)
        goto INNER;

      i++;
      int censor010 = i < 10;
      if (censor010)
        goto OUTER;

    }

  }

}
