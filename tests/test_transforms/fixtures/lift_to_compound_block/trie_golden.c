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
  (*censor01)[0] = &s;
  int i = 0;
  struct tnode *(*censor02)[10] = &r.c;
  struct tnode **censor03 = &(*censor02)[i];
  i++;
  int (*censor04)[10] = &(*censor03)->data;
  int d = (*censor04)[i];
}

