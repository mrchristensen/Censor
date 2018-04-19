typedef int size_t;
extern void *malloc (size_t __size);
int x;
struct rectangle
{
  int x;
  int y;
};
struct rectangle *makeRectangle(int x, int y)
{
  struct rectangle *r = (struct rectangle *) malloc(sizeof(struct rectangle));
  int *censor01 = &x;
  *censor01 = (*censor01) + 1;
  int *censor02 = &y;
  *censor02 = (*censor02) + 1;
  r->x = x;
  r->y = y;
  return r;
}

int main()
{
  struct rectangle *a = makeRectangle(2, 4);
  return 0;
}
