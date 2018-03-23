struct tnode
{
  int data[10];
  struct tnode *c[10];
};
int main()
{
  struct tnode r = {{0, 1, 2, 3, 4, 5, 6, 7, 8, 9}, {}};
  struct tnode s = {{0, 1, 2, 3, 4, 5, 6, 7, 8, 9}, {}};
  struct tnode *(*censor01)[10] = &r.c;
  struct tnode **censor02 = &(*censor01)[0];
  *censor02 = &s;
  int i = 0;
  struct tnode *(*censor03)[10] = &r.c;
  struct tnode **censor04 = &(*censor03)[i];
  i++;
  int (*censor05)[10] = &(*censor04)->data;
  int *censor06 = &(*censor05)[i];
  int d = *censor06;
}

