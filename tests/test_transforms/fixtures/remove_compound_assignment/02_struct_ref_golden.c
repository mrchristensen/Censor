struct rectangle
{
  int x;
  int y;
};

union Data
{
    int i;
    float f;
};

int main()
{
  struct rectangle rect = {0, 0};
  {
    int *censor01 = &rect.x;
    *censor01 = (*censor01) + 1;
  }
  struct rectangle *p = &rect;
  {
    int *censor02 = &p->y;
    *censor02 = (*censor02) + 1;
  }

  union Data d;
  d.i = 1;
  {
    int *censor03 = &d.i;
    *censor03 = (*censor03) + 1;
  }
  union Data *dp = &d;
  {
    float *censor04 = &dp->f;
    *censor04 = (*censor04) + 1;
  }

  return 0;
}
