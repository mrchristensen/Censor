typedef int size_t;
extern void *malloc (size_t __size);
struct rects {
  int x[10];
  int y[10];
};

int main() {
  struct rects *r = (struct rects*)malloc(sizeof(struct rects));
  int i = 0;
  int t = 0;
 OUTER:
  {
    int j = 0;
  INNER:
    {
      t = t + r->x[i = i + 1] + r->y[j = j + 1];
      if (j < 10)
        goto INNER;
      i++;
      if (i < 10)
        goto OUTER;
    }
  }
}
