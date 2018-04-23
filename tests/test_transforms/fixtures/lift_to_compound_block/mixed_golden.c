typedef int size_t;
extern void *malloc (size_t __size);
struct rects
{
  int x[10];
  int y[10];
};
int main()
{
  void *censor01 = malloc(sizeof(struct rects));
  struct rects *r = (struct rects *) censor01;
  int i = 0;
  int t = 0;
 OUTER:
  {
    int j = 0;
  INNER:
    {
      int (*censor02)[10] = &r->x;
      i = i + 1;
      int *censor03 = &(*censor02)[i];
      int censor04 = t + (*censor03);
      int (*censor05)[10] = &r->y;
      j = j + 1;
      int *censor06 = &(*censor05)[j];
      t = censor04 + (*censor06);
      int censor07 = j < 10;
      if (censor07)
        goto INNER;

      i++;
      int censor08 = i < 10;
      if (censor08)
        goto OUTER;

    }

  }

}
